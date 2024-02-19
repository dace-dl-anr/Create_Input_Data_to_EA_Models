import sklearn
from sklearn.model_selection import train_test_split
import os
import random
import pickle
import re
from Param import *
import sys
orig_stdout = sys.stdout
f = open('out.txt', 'w')
sys.stdout = f

# Check if the directory already exists
if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)

def create_att_rel_triples_files(data_path):
    """Creates 4 distinct file (2 for each KG), _att_triples files contain
    attribute triples of the KGs while _rel_triples files contain relation triples.
    """
    att_triples = []
    rel_triples = []
    with open(data_path,"r",encoding="utf-8") as f:
        for line in f:
            l = line.rstrip('\n').split(' ',2)[-1]
            l0 = line.rstrip('\n').split(' ',2)[0]
            if l[0] != "<":
                att_triples.append(line)
            else:
                if l0[0] != "_":
                    rel_triples.append(line)

    fname = data_path.split('/')[-1]
    fname = fname.split('_')[0]
    with open(PATH+fname+'_att_triples', 'w') as f:
        for p in att_triples:
            f.write(p)

    path = data_path.rpartition('/')[0]
    with open(path+'/'+fname+'_rel_triples', 'w') as f:
        for p in rel_triples:
            f.write(p)

def create_ent_id_files(fname):
    """Creates 2 files (1 for each KG) containing the KG entities, each of which
    assigned a unique ID.
    """
    count = 0
    for i in range(2):
        ent_dict = {}
        name = fname[i]
        with open(name, "r") as f:
            for line in f.readlines():
                h, r, t = line.rstrip('\n').split(' ',2)
                head_tail = []
                if not h.startswith('_:'):
                    h = h.strip('<>')
                    head_tail.append(h)
                    if t.startswith('<'):
                        t = t.strip('<>')
                        t = t.strip('> .')
                        head_tail.append(t)
                    for ent in head_tail:
                        if ent not in ent_dict:
                            e_id = count
                            ent_dict[ent] = str(e_id)
                            count+=1

        name = name.split(r"./raw_files/")[-1]
        with open(INPUT_DIR+name+"_ids", 'w') as f:
            for key in ent_dict.keys():
                f.write(ent_dict[key]+"\t"+key+"\n")

def create_ref_align():
    """Creates reference alignment file based on the unique IDs of entities.
    """
    ent_dict_1 = {}
    with open(INPUT_DIR+"ent_ids_1", "r") as f:
        for line in f.readlines():
            ent_id, ent_url = line.split('\t')
            ent_url = ent_url[:-1]
            ent_url = ent_url.strip()
            ent_dict_1[ent_url] = str(ent_id)

    ent_dict_2 = {}
    with open(INPUT_DIR+"ent_ids_2", "r") as f:
        for line in f.readlines():
            ent_id, ent_url = line.split('\t')
            ent_url = ent_url[:-1]
            ent_url = ent_url.strip()
            ent_dict_2[ent_url] = str(ent_id)

    pair_ent_ids = []
    with open("./raw_files/same_as", "r") as f:
            for line in f.readlines():
                ent1, ent2 = line.split()
                if ent1 in ent_dict_1:
                    pair_ent_ids.append(ent_dict_1[ent1]+'\t'+ent_dict_2[ent2])

    with open('./raw_files/ref_align', 'w') as f:
        for p in pair_ent_ids:
            f.write(p+'\n')

def create_sup_ref_pairs(fname):
    """Create train (for supervised learning) and test files by splitting the
    reference alignment
    """
    pairs_list = []
    with open(fname, "r") as f:
        for line in f.readlines():
            pairs_list.append(line)

    pair_train, pair_test = train_test_split(pairs_list, test_size=TEST_REF_SIZE , random_state=42)

    with open(INPUT_DIR+'sup_pairs', 'w') as f:
        for p in pair_train:
            f.write(p)

    with open(INPUT_DIR+'ref_pairs', 'w') as f:
        for p in pair_test:
            f.write(p)

def create_rel_ids_files(fname):
    """Create files assigning unique IDs to relation properties in each KG.
    """
    rel_dict1 = {}
    count = 0
    with open(fname[0], "r") as f:
        for line in f.readlines():
            h, r, t = line.rstrip('\n').split(' ',2)
            rel = r.strip('<>')
            if rel not in rel_dict1.keys():
                rel_dict1[rel] = str(count)
                count +=1
    name = fname[0].split(r"./raw_files/")[-1]
    with open(PATH+name+"_rel_ids", 'w') as f:
        for key in rel_dict1.keys():
            f.write(rel_dict1[key]+"\t"+key+"\n")

    rel_dict2 = {}
    with open(fname[1], "r") as f:
        for line in f.readlines():
            h, r, t = line.rstrip('\n').split(' ',2)
            rel = r.strip('<>')
            if rel not in rel_dict2.keys():
                rel_dict2[rel] = str(count)
                count +=1

    name = fname[1].split(r"./raw_files/")[-1]
    with open(PATH+name+"_rel_ids", 'w') as f:
        for key in rel_dict2.keys():
            f.write(rel_dict2[key]+"\t"+key+"\n")

def create_id_triples(fname):
    """Create 2 files (1 for each KG) containing relation triples shown by IDs.
    """
    for i in [1,2]:
        ent_dict = {}
        with open(INPUT_DIR+"ent_ids_"+str(i), "r") as f:
            for line in f.readlines():
                ent_id, ent_url = line.split('\t')
                ent_url = ent_url[:-1]
                ent_dict[ent_url] = str(ent_id)

        rel_dict = {}
        with open(PATH+"rel_ids_"+str(i), "r") as f:
            for line in f.readlines():
                rel_id, rel_url = line.split('\t')
                rel_url = rel_url[:-1]
                rel_dict[rel_url] = str(rel_id)

        spo_ids = []
        with open(fname[i-1], "r") as f:
            all_lines = f.readlines()
            random.shuffle(all_lines)
            for line in all_lines:
                h, r, t = line.rstrip('\n').split(' ',2)
                h = h.strip('<>')
                t = t.strip('<>')
                t = t.strip('> .')
                r = r.strip('<>')
                spo_ids.append(ent_dict[h]+'\t'+rel_dict[r]+'\t'+ent_dict[t])

        name = fname[i-1].split(r"./raw_files/")[-1]
        with open(INPUT_DIR+name+"_ids", 'w') as f:
            for spo in spo_ids:
                f.write(spo+'\n')

def create_description_dict_pick_file():
    """Creates a dictionary file of all entities in 2 datasets that "contains
    all the text attribute values. We remove ^^ValueTypes if existed in text."
    OR if HANDL_BLANK_NODE set to be True, it "Add desciption of blank nodes to
    the nodes that has relation with".
    """
    desc_dict = {}
    fnames = [DATASET+'_att_triples', 'en_att_triples']
    if HANDL_BLANK_NODE==0:
        for fname in fnames:
            with open(PATH+fname, "r") as f:
                for line in f.readlines():
                    h, r, t = line.rstrip('\n').split(' ',2)
                    h = h.strip('<>')
                    t = re.findall('\"(.+)\"', t)

                    if t:
                        t = t[0]
                        if h in desc_dict:
                            if t not in desc_dict[h]:
                                desc_dict[h] = desc_dict[h]+t+", "
                        else:
                            desc_dict[h] = t+", "

    if HANDL_BLANK_NODE==1:
        for fname in fnames:
            with open(INPUT_DIR+fname, "r") as f:
                for line in f.readlines():
                    h, r, t = line.rstrip('\n').split(' ',2)
                    h = h.strip('<>')
                    t = re.findall('\"(.+)\"', t)
                    if t:
                        t = t[0]
                        #print
                        if h in desc_dict:
                            if t not in desc_dict[h]:
                                desc_dict[h] = desc_dict[h]+t+", "
                        else:
                            desc_dict[h] = t+", "

        #Add blank keys to the dic that has relation with other blank nodes
        for fname in fnames:
            with open(INPUT_DIR+fname, "r") as f:
                for line in f.readlines():
                    h, r, t = line.rstrip('\n').split(' ',2)
                    h = h.strip('<>')
                    t = t.split()[0]
                    if h[0]=="_" and t[0] == '_':
                        if t in desc_dict:
                            if h in desc_dict:
                                if desc_dict[t] not in desc_dict[h]:
                                    desc_dict[h] = desc_dict[h]+desc_dict[t]+", "
                            else:
                                desc_dict[h] = desc_dict[t]+", "

        #Add desc of blank nodes to the nodes that has relation with them
        for fname in fnames:
            with open(INPUT_DIR+fname, "r") as f:
                for line in f.readlines():
                    h, r, t = line.rstrip('\n').split(' ',2)
                    h = h.strip('<>')
                    t = t.split()[0]
                    if t[0] == '_':
                        if t in desc_dict:
                            if h in desc_dict:
                                if desc_dict[t] not in desc_dict[h]:
                                    desc_dict[h] = desc_dict[h]+desc_dict[t]+", "
                            else:
                                desc_dict[h] = desc_dict[t]+", "

    #Remove lines that contain blank nodes
    for fname in fnames:
        not_blank_line = []
        with open(INPUT_DIR+fname, "r") as f:
            for line in f.readlines():
                if "_:" not in line:
                    not_blank_line.append(line)
        with open(INPUT_DIR+fname, "w") as f:
            for l in not_blank_line:
                f.write(l)
    blank_keys = []
    for key in desc_dict.keys():
        if key.startswith("_:"):
            blank_keys.append(key)
    for key in blank_keys:
        desc_dict.pop(key, None) #Remove blank nodes from node list

    print("Length of description dictionary:", len(desc_dict))
    with open(INPUT_DIR+DICT_NAME, 'wb') as handle:
        pickle.dump(desc_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    print("{} was created!".format(DICT_NAME))

if __name__ == '__main__':

    PATH_DATA = './raw_files/'+DATASET
    print("----------------create attribute and relation triples files--------------------")
    for fname in [PATH_DATA+'_triples', PATH+'en_triples']:
        create_att_rel_triples_files(fname)

    print("----------------create entity id files--------------------")
    fname = [PATH_DATA+'_triples', PATH+'en_triples']
    create_ent_id_files(fname)
    os.rename(INPUT_DIR+DATASET+'_triples_ids', INPUT_DIR+'ent_ids_1')
    os.rename(INPUT_DIR+'en_triples_ids', INPUT_DIR+'ent_ids_2')

    print("----------------create id reference alignment file--------------------")
    create_ref_align()
    os.popen('cp ./raw_files/ref_align {}ref_ent_ids'.format(INPUT_DIR))

    print("----------------create relation id files--------------------")
    fname = [PATH_DATA+'_rel_triples', PATH+'en_rel_triples']
    create_rel_ids_files(fname)
    os.rename(PATH+DATASET+'_rel_triples_rel_ids', PATH+'rel_ids_1')
    os.rename(PATH+'en_rel_triples_rel_ids', PATH+'rel_ids_2')




    print("----------------create id triples files--------------------")
    fname = [PATH_DATA+'_rel_triples', PATH+'en_rel_triples']
    create_id_triples(fname)
    os.rename(INPUT_DIR+DATASET+'_rel_triples_ids', INPUT_DIR+'triples_1')
    os.rename(INPUT_DIR+'en_rel_triples_ids', INPUT_DIR+'triples_2')

    #print("----------------create description dictionary file--------------------")
    #create_description_dict_pick_file()
    sys.stdout = orig_stdout
    f.close()
