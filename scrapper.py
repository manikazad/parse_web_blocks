import lxml
from lxml import etree
import urllib.request as urllib2

from lxml.html.clean import clean_html
from collections import Counter, defaultdict
from copy import deepcopy
import operator


flatten2 = lambda x : [z for y in x for z in y]


def traverse_dfs(tree):
    tree_string = []
    children = tree.iterchildren()
    for child in children:
        tree_string.append(child.tag)
        tree_string.append('pof')
        tree_string.extend(traverse_dfs(child))
    if tree_string == []:
        tree_string = ['end']
    return (tree_string)


def traverse_dfs_return_list_tree(tree):
    tree_string = []
    for child in tree.iterchildren():
        tree_string.append([child, 'pof', traverse_dfs_return_list_tree(child)])
    if tree_string == []:
        tree_string = ['end']
    return (tree_string)


def get_all_paths(tree_list):
    all_paths = []
    for path in tree_list:
        parent, pof, child = path
        current_path = [parent, pof]
        if child != ['end']:
            child_paths = get_all_paths(child)
            for cpath in child_paths:
                all_paths.append(current_path + cpath)
        else:
            all_paths.append(current_path + child)
    return all_paths


def convert_to_tags(path):
    tag_path = []
    for elem in path:
        if type(elem) == lxml.etree._Element:
            tag_path.append(elem.tag)
        else:
            tag_path.append(elem)
    return (tag_path)


def get_path_text(path):
    text_path = []
    for elem in path:
        if type(elem) == lxml.etree._Element:
            text = elem.text
            if text:
                if text.strip() != '':
                    text_path.append(text.strip())
    return (text_path)


def get_clean_page_list(page):
    cleaned_html = clean_html(page)
    tree = etree.HTML(cleaned_html)
    body = tree.getchildren()[0]
    body_list = traverse_dfs_return_list_tree(body)
    return (body_list)


def get_tag_sequences(all_tag_paths_joined):
    tag_path_indices = {}
    tag_path_counter = Counter()
    tag_index = 0
    for tag_path in all_tag_paths_joined:
        if tag_path not in tag_path_indices:
            tag_path_indices[tag_path] = tag_index
            tag_index += 1
        tag_path_counter[tag_path] += 1

    seq = [tag_path_indices[tag_path] for tag_path in all_tag_paths_joined]
    return (seq)


def get_seq_markov_matrix(seq):
    next_seq = defaultdict(Counter)
    seq_count = Counter(seq)
    prev = seq[0]
    next_seq[prev] = Counter()
    seq_count[prev] += 1

    for s in seq[1:]:
        next_seq[prev][s] += 1
        prev = s

    seq_prob = defaultdict(Counter)
    for key, vals in next_seq.items():
        count = seq_count[key]
        for nex, val in vals.items():
            seq_prob[key][nex] = val / count

    return (seq_prob)


def get_seq_index(seq):
    seq_index = defaultdict(list)
    for i, x in enumerate(seq):
        seq_index[x].append(i)
    return (seq_index)


def partition_tag_sequence(seq, seq_index):
    partitions = []
    new_part = []
    first = True
    for elem, index in seq_index.items():
        if first:
            new_part.append(elem)
            prev = index
            first = False
        else:
            if min(index) > max(prev):
                partitions.append(deepcopy(new_part))
                new_part = [elem]

            else:
                new_part.append(elem)
            prev = index

    seq_parts = []
    for part in partitions:
        seq_part = []
        for ind in part:
            seq_part.extend(seq_index[ind])
        seq_parts.append((min(seq_part), max(seq_part)))
    seqs = [seq[i:j + 1] for i, j in seq_parts]
    return (seqs)


def reverse(s):
    s = s.split()
    rev = s[::-1]
    return " ".join(rev)


def get_repeat_palindrome_sequences(seqs):
    sub_dict = {}
    palin_dict = {}
    MINLEN = 2
    MINCNT = 2
    for j, seq in enumerate(seqs):
        s = seq
        s_s = " ".join([str(x) for x in seq])
        subd = {}
        palind = {}
        for sublen in range(MINLEN, int(len(s) / MINCNT)):
            for i in range(0, len(s) - sublen):
                sub = " ".join([str(x) for x in s[i:i + sublen]])
                cnt = s_s.count(sub)
                if cnt >= MINCNT and sub not in subd:
                    subd[sub] = cnt
                if sub == reverse(sub) and sub not in palind:
                    palind[sub] = cnt
        sub_dict[j] = subd
        palin_dict[j] = palind

    return sub_dict, palin_dict


def remove_repeat_larger_seq(seq_dict):
    repeat_seq = set()
    remaining_seqs = {}
    for ind, subseqs in seq_dict.items():
        seq_list = list(subseqs.keys())
        seq_list2 = deepcopy(seq_list)
        for i, seq in enumerate(subseqs.keys()):
            for seq1 in seq_list:
                if seq != seq1 and seq1.count(seq) * len(seq.split()) == len(seq1.split()):
                    seq_list2.remove(seq1)
                    repeat_seq.add(seq)

                if seq != seq1 and seq1.count(seq) >= 1:
                    try:
                        seq_list2.remove(seq)
                    except ValueError:
                        pass

            seq_list = deepcopy(seq_list2)
        remaining_seqs[ind] = seq_list2

    return (repeat_seq, remaining_seqs)


def remove_smaller_subseqs(seq_dict):
    remaining_seqs = {}
    for ind, subseqs in seq_dict.items():
        seq_list = list(subseqs.keys())
        seq_list2 = deepcopy(seq_list)
        for i, seq in enumerate(subseqs.keys()):
            for seq1 in seq_list:
                if seq != seq1 and seq1.count(seq) >= 1:
                    seq_list2.remove(seq)
                    break
            seq_list = deepcopy(seq_list2)
        remaining_seqs[ind] = seq_list2
    return (remaining_seqs)


def get_relevant_sequence_portions(seq, all_seqs, all_elem_paths):
    rel_seq_index_tuple = []
    n = len(seq)
    for sub in all_seqs:
        l = len(sub.split())
        for i in range(0, n - l + 1):
            part = [str(x) for x in seq[i: i + l]]
            if part == sub.split():
                rel_seq_index_tuple.append((i, i + l))
    rel_seq_index_tuple = sorted(rel_seq_index_tuple, key=operator.itemgetter(0))

    seq_index = []
    unique_seq_indices = []
    first = True
    for ind_tup in rel_seq_index_tuple:
        if first:
            first = False
            seq_index = list(ind_tup)
        if seq_index[1] > ind_tup[0]:
            if seq_index[1] < ind_tup[1]:
                seq_index[1] = ind_tup[1]
        elif seq_index[1] < ind_tup[0]:
            unique_seq_indices.append(deepcopy(seq_index))
            seq_index = list(ind_tup)

    seq_elem_paths = []
    for tup in unique_seq_indices:
        s, e = tup
        seq_elem_paths.append(all_elem_paths[s:e + 1])

    return seq_elem_paths


def get_block_sequence_texts(seq_elem_paths):
    seq_texts = []
    for elem_paths in seq_elem_paths:
        path_texts = []
        for path in elem_paths:
            path_text = get_path_text(path)
            if path_text:
                path_texts.append(path_text)
        non_overlapping_text = []
        first = True
        prev = []
        for text in path_texts:
            if first:
                non_overlapping_text.append(list(set(text)))
                prev = text
                first = False
            else:
                diff = set(text).difference(prev)
                if diff:
                    non_overlapping_text.append(list(diff))
                prev = text
        seq_texts.append(non_overlapping_text)
    return seq_texts


def scrap_for_text(page):

    body_list = get_clean_page_list(page)
    all_elem_paths = get_all_paths(body_list)
    all_tag_paths = [convert_to_tags(path) for path in all_elem_paths]
    # text_paths = [get_path_text(path) for path in all_elem_paths ]
    all_tag_paths_joined = ["_".join(path) for path in all_tag_paths]
    seq = get_tag_sequences(all_tag_paths_joined)

    seq_index = get_seq_index(seq)
    seqs = partition_tag_sequence(seq, seq_index)

    sub_dict, palin_dict = get_repeat_palindrome_sequences(seqs)
    repeat_seqs, remaining_seq = remove_repeat_larger_seq(sub_dict)
    palins = remove_smaller_subseqs(palin_dict)

    all_seqs = list(repeat_seqs) + flatten2([vals for ind, vals in remaining_seq.items()]) + flatten2([vals for ind, vals in palins.items()])

    seq_elem_paths = get_relevant_sequence_portions(seq, all_seqs, all_elem_paths)
    seq_texts = get_block_sequence_texts(seq_elem_paths)
    return seq_texts

