 #    Copyright (C) 2014 MongoDB Inc.
 #
 #    This program is free software: you can redistribute it and/or  modify
 #    it under the terms of the GNU Affero General Public License, version 3,
 #    as published by the Free Software Foundation.
 #
 #    This program is distributed in the hope that it will be useful,
 #    but WITHOUT ANY WARRANTY; without even the implied warranty of
 #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 #    GNU Affero General Public License for more details.
 #
 #    You should have received a copy of the GNU Affero General Public License
 #    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re

function_pipeline = [
	{
		"$project" : {
			"file" : 1,
			"git_hash" : 1,
			"build_id" : 1,
			"dir" : 1,
			"functions" : 1
		}
	},
	{
		"$unwind" : "$functions"
	},
	{
		"$group" : {
			"_id" : {
				"file" : "$file",
				"git_hash" : "$git_hash",
				"build_id" : "$build_id",
				"line" : "$functions.ln",
				"dir" : "$dir"
			},
			"count" : {
				"$sum" : "$functions.ec"
			}
		}
	},
	{
		"$group" : {
			"_id" : {
				"file" : "$_id.file",
				"git_hash" : "$_id.git_hash",
				"build_id" : "$_id.build_id",
				"line" : "$_id.line",
				"dir" : "$_id.dir"
			},
			"hit" : {
				"$sum" : {
					"$cond" : {
						"if" : {
							"$eq" : [
								"$count",
								0
							]
						},
						"then" : 0,
						"else" : 1
					}
				}
			}
		}
	},
	{
		"$group" : {
			"_id" : {
				"dir" : "$_id.dir",
				"git_hash" : "$_id.git_hash",
				"build_id" : "$_id.build_id"
			},
			"func_count" : {
				"$sum" : 1
			},
			"func_cov_count" : {
				"$sum" : "$hit"
			}
		}
	}
]

line_pipeline = [
	{
		"$project" : {
			"file" : 1,
			"git_hash" : 1,
			"build_id" : 1,
			"dir" : 1,
			"lc" : 1
		}
	},
	{
		"$unwind" : "$lc"
	},
	{
		"$group" : {
			"_id" : {
				"file" : "$file",
				"git_hash" : "$git_hash",
				"build_id" : "$build_id",
				"line" : "$lc.ln",
				"dir" : "$dir"
			},
			"count" : {
				"$sum" : "$lc.ec"
			}
		}
	},
	{
		"$group" : {
			"_id" : {
				"file" : "$_id.file",
				"line" : "$_id.line",
				"git_hash" : "$_id.git_hash",
				"build_id" : "$_id.build_id",
				"dir" : "$_id.dir"
			},
			"hit" : {
				"$sum" : {
					"$cond" : {
						"if" : {
							"$eq" : [
								"$count",
								0
							]
						},
						"then" : 0,
						"else" : 1
					}
				}
			}
		}
	},
	{
		"$group" : {
			"_id" : {
				"dir" : "$_id.dir",
				"git_hash" : "$_id.git_hash",
				"build_id" : "$_id.build_id"
			},
			"line_count" : {
				"$sum" : 1
			},
			"line_cov_count" : {
				"$sum" : "$hit"
			}
		}
	}
]

file_line_pipeline = [
	{
		"$project" : {
			"file" : 1,
			"lc" : 1
		}
	},
	{
		"$unwind" : "$lc"
	},
	{
		"$group" : {
			"_id" : {
				"file" : "$file",
				"line" : "$lc.ln"
			},
			"count" : {
				"$sum" : "$lc.ec"
			}
		}
	},
        {
                "$sort" : {
                        "_id.file": 1
                }
        }

]

file_func_pipeline = [
	{
		"$project" : {
			"file" : 1,
			"functions" : 1
		}
	},
	{
		"$unwind" : "$functions"
	},
	{
		"$group" : {
			"_id" : {
				"file" : "$file",
				"function" : "$functions.nm"
			},
			"count" : {
				"$sum" : "$functions.ec"
			}
		}
	},
        {
                "$sort" : {
                        "_id.file": 1
                }
        }

]

file_comp_pipeline = [
	{
		"$project" : {
			"file" : 1,
			"lc" : 1
		}
	},
	{
		"$unwind" : "$lc"
	},
	{
		"$group" : {
			"_id" : {
				"file" : "$file",
				"line" : "$lc.ln"
			},
			"count" : {
				"$sum" : "$lc.ec"
			}
		}
	},
        {
                "$sort" : {
                        "_id.file": 1
                }
        }

]

testname_pipeline = [
	{
		"$project" : {
			"build_id" : 1,
			"git_hash" : 1,
			"test_name" : 1
		}
	},
	{
		"$group" : {
			"_id" : {
				"git_hash" : "$git_hash",
				"build_id" : "$build_id"
			},
			"test_names" : {
				"$addToSet" : "$test_name"
			}
		}
	}
]

