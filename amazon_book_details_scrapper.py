import requests
from bs4 import BeautifulSoup
import csv
from collections import defaultdict
import pandas as pd
import math
import matplotlib.pyplot as plt
plt.close('all')

print("*************************\n\n")
train_data = []
first_row = True
not_found = 0
isbn_set = set()
author_num_books_dict = defaultdict(int)


with open('amazon_1_end.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    #train_data.append(['url', 'title', 'pub_date', 'price', 'isbn', 'num_authors', 'num_pages'])
    train_data.append(['title', 'pub_date', 'price', 'isbn', 'num_authors', 'num_pages', 'pub_year', 'publisher', 'all_authors', 'authors_exp'])

    for row in readCSV:
        if first_row:
            first_row = False
            continue

        authors = row[6]
        book_specs = row[7]
        soup = BeautifulSoup(authors, 'html.parser')
        #soup.find("span", {"class": "author notFaded"}).findAll("a", recursive=False)
        num_authors = 0

        if soup == None:
            not_found += 1
            continue

        all_authors = []

        for node in soup.findAll("a", {"class": "a-link-normal"}):
            if len(node.contents) > 1:
                continue

            node_contents = ''.join(node.contents)
            if 'Visit Amazon' in node_contents or 'search results' in node_contents or 'Learn about' in node_contents:
                continue

            author_num_books_dict[node_contents.strip()] += 1
            all_authors.append(node_contents.strip())
            num_authors += 1

        #print('num_authors = ', num_authors)

        soup = BeautifulSoup(book_specs, 'html.parser')

        num_pages = None
        publisher = None
        isbn = row[5].strip()
        price = row[4].replace('$', '').strip().replace(' ','')

        for node in soup.findAll("li"):
            if 'pages' in (node.contents[0].text):
                num_pages = node.contents[0].text.split()[-2]
                #print('num pages = ', num_pages)

            if 'Publisher' in (node.contents[0].text):
                publisher = node.contents[0].text.split(':')[1].split(';')[0]
                publisher = publisher.split(' (')[0].strip()
                #print(publisher)
                #print('publisher = ', node.contents[0].text.split(';')[0].split(':')[1].strip())

        pub_date = row[3].strip()
        pub_year = pub_date.split(',')[-1].strip()

        if num_pages == None or publisher == None or price == '' or isbn in isbn_set or num_authors == 10 or int(pub_year) == 2021:
            not_found += 1
            #print(row[1])

        else:
            price = float(price)
            isbn_set.add(isbn)

            #train_data.append([row[1].strip(), row[2].strip(), row[3].strip(), price, isbn, num_authors, num_pages])
            num_pages = int(num_pages)
            if num_pages < 51:
                num_pages = 50

            else:
                num_pages = math.ceil(num_pages / 100) * 100
                if num_pages >= 1000:
                    num_pages = 950

            if num_authors >=6:
                num_authors = 6

            pub_year = int(pub_year)

            if pub_year < 2005:
                pub_year = 2005

            all_authors = ','.join(all_authors)

            train_data.append([row[2].strip(), row[3].strip(), price, isbn, num_authors, num_pages, pub_year, publisher, all_authors])
        #print('*****************************************\n\n')


print(not_found)
print(len(isbn_set))
i = 0

while(i < len(train_data)):
    if i == 0:
        i += 1
        continue

    row = train_data[i]
    authors = row[-1]
    authors_exp = 0

    for author in authors.split(','):
        exp = author_num_books_dict[author]
        authors_exp += author_num_books_dict[author]

    if authors_exp == 0:
        authors_exp = 1

    train_data[i].append(authors_exp)
    i += 1


file = open('amazon_books_price_num_authors.csv', 'w+', newline='')


# writing the data into the file
with file:
    write = csv.writer(file)
    write.writerows(train_data)

print(author_num_books_dict)


books_df = pd.read_csv('amazon_books_price_num_authors.csv')

res = books_df.groupby('authors_exp')
authors_exp_price_relationship = res.mean().sort_values(by='authors_exp')
print('\n', authors_exp_price_relationship)
#authors_exp_price_relationship.to_csv('authors_exp_price_relationship.csv')
authors_exp_price_relationship.reset_index().plot(x='authors_exp', y='price', kind='bar')
plt.show()


res = books_df.groupby('num_authors')
authors_price_realtionship =  res.mean().sort_values(by='num_authors')
print('\n', authors_price_realtionship)
#authors_price_realtionship.to_csv('authors_price_realtionship.csv')
authors_price_realtionship.reset_index().plot(x='num_authors', y='price', kind='bar')
plt.show()

res = books_df.groupby('num_pages')
pages_price_relationship = res.mean().sort_values(by='num_pages')
print('\n', pages_price_relationship)
#pages_price_relationship.to_csv('pages_price_realationship.csv')
pages_price_relationship.reset_index().plot(x='num_pages', y='price', kind='bar')
plt.show()

res = books_df.groupby('pub_year')
pub_year_price_relationship = res.mean().sort_values(by='pub_year')
print('\n', pub_year_price_relationship)
#pub_year_price_relationship.to_csv('pub_year_price_realationship.csv')
pub_year_price_relationship.reset_index().plot(x='pub_year', y='price', kind='bar')
plt.show()

res = books_df.groupby('publisher')
publisher_price_relationship = res.mean()

res = books_df.groupby('publisher')
publisher_count_relationship = res.count()

publisher_count_price_relationsip = pd.merge(publisher_price_relationship, publisher_count_relationship, on='publisher')
publisher_count_price_relationsip = publisher_count_price_relationsip.sort_values(by='price_x', ascending=False).head(10)
print(publisher_count_price_relationsip)
publisher_count_price_relationsip.to_csv('publisher_count_price_relationsip.csv')
publisher_count_price_relationsip.reset_index().plot(x='publisher', y='price_x', kind='bar')
plt.show()