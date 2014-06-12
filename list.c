#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "list.h"

/* This file consists of functions designed to manipulate
 * a linked list structure. The linked list consists of a
 * struct List, which keeps track of the first and last
 * elements of the list. Elements of the list are represented
 * by struct Node. A node consists of a pointer to the next
 * node, and pointers to the key, value, and type of the value
 * stored by the node. This linked list is designed to output
 * its data in the form of a JSON object.
 */

static void die (const char *message) {
    perror(message);
    exit(1);
}

void initList (struct List *list) {
    list->front = NULL;
    list->back = NULL;
}

int isEmptyList (const struct List *list) {
    return list->front == NULL;
}

/* Determine whether list or its sublists,
 * if present, has an empty list as its 
 * data value, or is an empty list itself. 
 * Used to prevent printing trailing commas.
 */
static int isEmptyListChain(const struct List *list) {
    if (!isEmptyList(list)) {
        if (list->front->value != NULL) {
           if (strcmp(list->front->type, "list") == 0 || 
               strcmp(list->front->type, "object") == 0) 
               return isEmptyListChain((struct List *) list->front->value);
           else
               return 0;
        }
        else
            return 1;
    }

    return 1;
}

/* Add key/value entry to list. type represents the type of the 
 * value.
 */
void addToList (struct List *list, const char *key, const void *value,
                const char *type) {
    if ((strcmp(type, "list") == 0 ||
         strcmp(type, "object") == 0) && 
        isEmptyListChain((const struct List *) value))
        return;

    struct Node *newNode = (struct Node *) malloc(sizeof(struct Node));
    if (newNode == NULL) {
        die("malloc failed");
    }
   
    if (isEmptyList(list)) {
        list->front = newNode; 
        list->back = newNode;
    }

    else {
        list->back->next = newNode;
        list->back = newNode;
    }

    newNode->type = type;
    newNode->next = NULL;
    
    // Make copies of the key and value arguments
    newNode->key = (char *) malloc(strlen(key) + 3);
    if (newNode->key == NULL) {
        die("malloc failed");
    }
    strcpy(newNode->key, "\"");
    strcpy(newNode->key + 1, key);
    strcpy(newNode->key + strlen(key) + 1, "\"");

    if (strcmp(newNode->type, "long") == 0) {
        newNode->value = malloc(sizeof(long));
        *((long *) newNode->value) = *(const long *)value;
    }

    if (strcmp(newNode->type, "string") == 0) {
        newNode->value = malloc(strlen((const char *) value) + 3);
        strcpy((char *) newNode->value, "\"");
        strcpy((char *) newNode->value + 1, (const char *) value);
        size_t len = strlen((const char *) value);
        strcpy((char *) newNode->value + len + 1, "\"");
    }

    /* Note that adding a node with data type "list" will
     * only work if the list to be added is in its final form
     * prior to adding. The copy of the list generated by 
     * addToList will reflect the data that was present in the
     * source list at the time of the copy.
     * Lists and objects are stored the same way, but printed
     * differently.
     */
    if (strcmp(newNode->type, "list") == 0 ||
        strcmp(newNode->type, "object") == 0) {
        newNode->value = malloc(sizeof(struct List));
        struct List *newNodeList = (struct List *) newNode->value;
        const struct List *argList = (const struct List *) value;
        newNodeList->front = argList->front;
        newNodeList->back = argList->back;
    }

    if (strcmp(newNode->type, "char") == 0) {
        newNode->value = malloc(sizeof(char));
        *((char *) newNode->value) = *(const char *)value;
    }

    if (strcmp(newNode->type, "unsigned") == 0) {
        newNode->value = malloc(sizeof(unsigned));
        *((unsigned *) newNode->value) = *(const unsigned *)value;
    }

    if (newNode->value == NULL) {
        die("malloc failed");
    }

}

static int isSubstantialInfo (struct List *list) {
    if (list->front->next == NULL)
        return 0;
    else
        return 1;
}

/* Helper function for printing the data in a struct List. Prints
 * data in the Node and then frees data and Node.
 */
static void printAndDeleteNode (struct Node *node, FILE *file) {
    int moreDataExists = 1;
    struct Node *next = node->next;
    
    // Determine whether to proceed to next recursive call.
    if (next == NULL) {
        moreDataExists = 0;
    }
   
    // If node has List as its value, recursively print list. 
    // Only print list if list is not empty.
    if (strcmp(node->type, "list") == 0 && 
        !isEmptyList((struct List *) node->value)) {
        if (strcmp(node->key, "\"\"") != 0) 
            fprintf(file, "%s: [", node->key);
        else
            fprintf(file, "[");
        struct List *subList = (struct List *) node->value;
        printAndDeleteNode(subList->front, file);
        fprintf(file, "]");
    }
 
    if (strcmp(node->type, "object") == 0 && 
        !isEmptyList((struct List *) node->value)) {
        if (strcmp(node->key, "\"\"") != 0) 
            fprintf(file, "%s: {", node->key);
        else
            fprintf(file, "{");
        struct List *subList = (struct List *) node->value;
        printAndDeleteNode(subList->front, file);
        fprintf(file, "}");
    }
   
    if (strcmp(node->type, "long") == 0) {
       fprintf(file, "%s: %lu", node->key, *(long *) node->value);
    }

    if (strcmp(node->type, "string") == 0) {
        fprintf(file, "%s: %s", node->key, (char *) node->value);
    }

    if (strcmp(node->type, "char") == 0) {
        fprintf(file, "%s: %c", node->key, *(char *) node->value);
    }

    if (strcmp(node->type, "unsigned") == 0) {
        fprintf(file, "%s: %u", node->key, *(unsigned *) node->value);
    }

    // Done printing current node, free allocated data.
    free(node->key);
    free(node->value);
    free(node);

    if (moreDataExists) {
        fprintf(file, ", ");
        printAndDeleteNode(next, file);
    }
}

/* Print elements in a list as a JSON object, deleting them
 * as they are printed. Return 1 if print was successful, 
 * 0 if print was unsuccessful.
 */
int printAndDeleteList (struct List *list, FILE *file) {
    // Don't print anything if list has no coverage info.
    if (!isSubstantialInfo(list)) {
        free(list->front->key);
        free(list->front->value);
        free(list->front);
        return 0;
    }

    fprintf(file, "{");
    printAndDeleteNode(list->front, file);
    fprintf(file, "}");
    fflush(file);
    return 1;
}

