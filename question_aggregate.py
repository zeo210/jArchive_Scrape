import csv
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
clue_dir = os.path.join(base_dir, 'clues')
fieldnames = ['episodeID', 'category', 'value', 'clues', 'answer']
categories = dict()  # value represents the number of answers
clues = dict()
category_answer_set = set()
combined_categories_set = set()


def compile_clues():
    csv_list = os.listdir(clue_dir)
    for csv_file_name in csv_list:
        with open(os.path.join(clue_dir, csv_file_name), encoding='utf-8') as open_csv_file:
            csv_reader = csv.reader(open_csv_file)
            next(csv_reader)
            for row in csv_reader:
                if row[0] not in clues:
                    clues[row[0]] = 1
                else:
                    clues[row[0]] += 1
                if row[0] + row[3].lower() not in category_answer_set:
                    category_answer_set.add(row[0] + row[3].lower())
                    if row[0] not in categories:
                        categories[row[0]] = 1
                    else:
                        categories[row[0]] += 1


def select_categories(answer_compare,
                 compare_answer_value,
                 clue_compare,
                 compare_clue_value):
    selected_categories = set()
    for key, value in sorted(categories.items(), key=lambda x: (-x[1], x[0])):
        if answer_compare(value, compare_answer_value) and \
           clue_compare(clues[key], compare_clue_value):
            selected_categories.add(key)
            if key not in combined_categories_set:
                combined_categories_set.add(key)
            print(key)
    return selected_categories


def output_clues(selected_categories, target_directory):
    csv_list = os.listdir(clue_dir)
    with open(target_directory, 'w', encoding='utf-8', newline='') as clue_csv_file:
        clue_csv_writer = csv.writer(clue_csv_file, quoting=csv.QUOTE_ALL)
        clue_csv_writer.writerow(fieldnames)

        for csv_file_name in csv_list:
            with open(os.path.join(clue_dir, csv_file_name), encoding='utf-8') as open_csv_file:
                csv_reader = csv.reader(open_csv_file)
                next(csv_reader)
                for row in csv_reader:
                    if row[0] in selected_categories:
                        clue_csv_writer.writerow([csv_file_name[:-4]] + row)


def greater_than(check_value, comparing_value):
    return check_value > comparing_value


def less_than(check_value, comparing_value):
    return check_value < comparing_value


def equals(check_value, comparing_value):
    return check_value == comparing_value


def in_range(check_value, comparing_value):
    return comparing_value[0] < check_value < comparing_value[1]

if __name__ == "__main__":
    compile_clues()
    output_clues(select_categories(equals, 3,
                                   greater_than, 5),
                 os.path.join(*[base_dir,
                                'test_set',
                                '3_answers_multiple_clues.csv']))
    output_clues(select_categories(in_range, (4, 8),
                                   greater_than, 9),
                 os.path.join(*[base_dir,
                                'test_set',
                                'low_answer_high_clue_count.csv']))
    output_clues(combined_categories_set, os.path.join(*[base_dir,
                                                         'all_clues.csv']))

