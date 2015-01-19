import csv
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
clue_dir = os.path.join(base_dir, 'clues')
fieldnames = ['episodeID', 'category', 'value', 'clues', 'answer']
categories = dict()
clues = dict()
category_answer_set = set()

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
            if row[0] + row[3] not in category_answer_set:
                category_answer_set.add(row[0] + row[3])
                if row[0] not in categories:
                    categories[row[0]] = 1
                else:
                    categories[row[0]] += 1
for key, value in sorted(categories.items(), key=lambda x: (-x[1], x[0])):
    if value < 3:
        categories.pop(key)
    elif clues[key] < 15:
        categories.pop(key)
    else:
        print("{}: {} | {}".format(key, value, clues[key]))

csv_list = os.listdir(clue_dir)
with open(os.path.join(base_dir, 'clues.csv'),
          'w', encoding='utf-8', newline='') as clue_csv_file:
    clue_csv_writer = csv.writer(clue_csv_file, quoting=csv.QUOTE_ALL)
    clue_csv_writer.writerow(fieldnames)

    for csv_file_name in csv_list:
        with open(os.path.join(clue_dir, csv_file_name), encoding='utf-8') as open_csv_file:
            csv_reader = csv.reader(open_csv_file)
            next(csv_reader)
            for row in csv_reader:
                if row[0] in categories:
                    clue_csv_writer.writerow([csv_file_name[:-4]] + row)