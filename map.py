import sys

with open(sys.argv[1]) as f:
    ans_list = f.readlines()
ans_list = [x.strip() for x in ans_list]
ans_list.pop(0)
ans = dict()
for line in ans_list:
    ans[line[:3]] = line.split(',')[1].split(' ')

# ans/rank[queryID] -> [ doc1, doc2, ... ]

with open(sys.argv[2]) as f:
    my_rank = f.readlines()
my_rank = [x.strip() for x in my_rank]
my_rank.pop(0)
rank = dict()
for line in my_rank:
    rank[line[:3]] = line.split(',')[1].split(' ')

acc = 0
# Calculate map
for query in rank:
    correct_doc = 0
    total_doc = 0
    precision = 0
    for doc in rank[query]:
	total_doc = total_doc + 1
	if doc in ans[query]:
	    correct_doc = correct_doc + 1
            precision += (correct_doc / float(total_doc))
    if correct_doc == 0:
        pass
    else:
        precision /= correct_doc
    #print "correctdoc :" + str(correct_doc)
    #print "total_doc  :" + str(total_doc)
    acc += precision

print 'acc = ' + str(acc/len(rank)) 

