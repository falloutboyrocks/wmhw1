# -*- coding: utf-8 -*-

import sys
import math
import operator
# Functions
def parse_docID(doc_path):
    with open(doc_path) as f:
        lines = f.readlines()
    lines = [x.strip() for x in lines]
    for line in lines:
        if '<id>' in line:
            return line.split('<id>')[1][:-5]

def wordcount_doc(doc_path):
    with open(doc_path) as f:
        doc = f.read().replace('\n', '')
    return len(doc.split('</text>')[0].split('<text>')[1].replace('<p>', '').replace('</p>', ''))

#############################################

# Store command line argument
i = 0
while i < len(sys.argv):
    if sys.argv[i] == '-r':
        Rocchio = True
    elif sys.argv[i] == '-i':
        query_file = sys.argv[i+1]
        i = i + 1
    elif sys.argv[i] == '-o':
        ranked_list = sys.argv[i+1]
        i = i + 1
    elif sys.argv[i] == '-m':
        model_dir = sys.argv[i+1]
        i = i + 1
    elif sys.argv[i] == '-d':
        NTCIR_dir = sys.argv[i+1]
        i = i + 1
    i = i + 1

# Hyperparameter
k = 1.2
b = 0.75
rank_num = 100
t_weight = float(sys.argv[len(sys.argv) - 2])
q_weight = float(sys.argv[len(sys.argv) - 1])

# Important Variable
avg_wordcount = 0

# Map: fileID -> 0.docID 1.fileLength
fileID_docID = dict()
with open(model_dir + '/file-list') as f:
    file_list = f.readlines()
file_list = [x.strip() for x in file_list]
filecount = len(file_list)
for i in range(len(file_list)):
    info = []
    info.append(parse_docID(file_list[i]))
    word_count = wordcount_doc(file_list[i])
    avg_wordcount += word_count
    info.append(word_count)
    fileID_docID[str(i)] = info
avg_wordcount /= len(file_list)

# Map: vocab ->  vocabID
vocab_vocabID = dict()
with open(model_dir + '/vocab.all') as f:
    vocab_list = f.readlines()
vocab_list = [x.strip() for x in vocab_list]
for i in range(1, len(vocab_list)):
    vocab_vocabID[vocab_list[i].decode(vocab_list[0])] = str(i)


# Set up inverted file of unigram & bigram
unigram_record = dict()
bigram_record = dict()
unigram_freq = dict()

with open(model_dir + '/inverted-file') as f:
    inverted_list = f.readlines()
inverted_list = [x.strip() for x in inverted_list]
cursor = 0
while cursor < len(inverted_list):
    info = inverted_list[cursor].split(' ')
    cursor = cursor + 1
    if info[1] == '-1':			# unigram
	unigram_record[info[0]] = []
	unigram_freq[info[0]] = int(info[2])
        for i in range(int(info[2])):
            record = []
	    record.append(inverted_list[cursor].split(' ')[0])
	    record.append(int(inverted_list[cursor].split(' ')[1]))
	    unigram_record[info[0]].append(record)
	    cursor = cursor + 1
    else:				# bigram
        bigram_record[info[0] + ':' + info[1]] = []
	for i in range(int(info[2])):
	    record = []
	    record.append(inverted_list[cursor].split(' ')[0])
	    record.append(int(inverted_list[cursor].split(' ')[1]))
	    bigram_record[info[0] + ':' + info[1]].append(record)
	    cursor = cursor + 1

# Process Queryfile
with open(query_file) as f:
    queries = f.read().replace('\n', '')
queries = queries.split('<topic>')
queries.pop(0)
query_list = []
for q in queries:
    query = []
    query.append(q.split('</number>')[0].split('<number>')[1].decode('utf8')) 
    query.append(q.split('</title')[0].split('<title>')[1].decode('utf8'))
    query.append(q.split('</question>')[0].split('<question>')[1].decode('utf8'))
    query.append(q.split('</narrative>')[0].split('<narrative>')[1].decode('utf8'))
    query.append(q.split('</concepts>')[0].split('<concepts>')[1].decode('utf8'))
    query_list.append(query)

# TF(Okapi)-IDF
IDF = dict()
biIDF = dict()
for vocabID in unigram_record:
    for record in unigram_record[vocabID]:
        wordcount = fileID_docID[record[0]][1]
	record[1] = ( (k+1) * record[1] ) / ( record[1] + k * (1 - b + b * wordcount / avg_wordcount) )
    IDF[vocabID] = math.log( filecount / len(unigram_record[vocabID]) )

for word in bigram_record:
    for record in bigram_record[word]:
        wordcount = fileID_docID[record[0]][1]
	record[1] = ( (k+1) * record[1] ) / ( record[1] + k * (1 - b + b * wordcount / avg_wordcount) )
    biIDF[word] = math.log( filecount / len(bigram_record[word]) )
    
# Calculate similarity
f = open(ranked_list, 'w')
f.write('query_id,retrieved_docs\n')
for q in query_list:
    query_id = q[0][len(q[0])-3:]
    f.write(query_id + ', ')
    file_score = dict()
    q[4] = q[4].replace(u'、', ' ').replace(u'。', '')
    q[4] = q[4].split(' ')
    bigram = []
    for word in q[4]:
	cur = 0
        while cur < len(word) - 1:
	    bigram.append(word[cur:cur+2])
	    cur = cur + 1
    for word in bigram:
	weight = 1
	if word in q[1]:
	    weight *= t_weight	    
	if word in q[2]:
	    weight *= q_weight
	word1 = word[0]
	word2 = word[1]
	if (not word1 in vocab_vocabID) or (not word2 in vocab_vocabID):
	    print word
	    continue
        word = vocab_vocabID[word1] + ':' + vocab_vocabID[word2]
	if not word in bigram_record:
	    print word
	    continue
	else:
	    for file_record in bigram_record[word]:
	        if not file_record[0] in file_score:
                    file_score[file_record[0]] = 0
	        file_score[file_record[0]] += file_record[1] * biIDF[word] * weight
    sorted_list = sorted(file_score.items(), key=operator.itemgetter(1))
    sorted_list.reverse()
    for i in range(rank_num):
        f.write(fileID_docID[sorted_list[i][0]][0] + ' ')
    f.write('\n')





    







