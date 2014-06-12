#ifndef _LIST_H_
#define _LIST_H_
struct Node {
    struct Node *next;

    char *key;
    void *value;
    const char *type;
};

struct List {
    struct Node *front;
    struct Node *back;
};

void initList(struct List *);
int isEmptyList(const struct List *);
void addToList(struct List *, const char *, const void *, 
               const char *);
int printAndDeleteList(struct List *, FILE *);
#endif
