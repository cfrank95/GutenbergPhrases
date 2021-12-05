import requests
import random
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
import threading
import time


# Find all missing indexes using the catalog (some may not be missing but the information is needed)
#   This has been removed and the response of the page is used to verify if the book is a valid index
# def missing_indexes(csv, num: int) -> set:
#     missing = set()
#
#     index_cache = set()
#     for line in csv['Text#']:
#         index_cache.add(line)
#
#     for i in range(1, num + 1):
#         if i not in index_cache:
#             missing.add(i)
#
#     print(missing)
#     return missing


# URL of all books will be https://www.gutenberg.org/ebooks/{1 - 66877}
# URL of all txt files for all books https://www.gutenberg.org/files/{1 - 66877}/{1 - 66877}.txt
#   Which first needs to be accessed at : https://www.gutenberg.org/files/{1 - 66877}/
#       Due to the formatting of URLS at txt page

if __name__ == '__main__':
    stop_words = set(stopwords.words())
    stop_words.add("project")
    stop_words.add("gutenberg")
    stop_words.add("gutenbergm")
    stop_words.add("gutenbergtm")

    def main_process():     # This will be used in case the random book cannot be encoded/ decoded properly
        # Find random book index
        num_books = 66080
        book_num = random.randint(1, num_books)
        # read_csv = pd.read_csv("res/pg_catalog.csv", low_memory=False)

        # Connect to that book's file index
        url = f"https://www.gutenberg.org/files/{book_num}/"
        pre_r = requests.get(url)

        while pre_r.status_code != 200:
            book_num = random.randint(1, num_books)

        # Find txt extension to add into txt file url
        pre_soup = BeautifulSoup(pre_r.text, 'html.parser')

        link_ext = ''
        for link in pre_soup.find_all('a'):
            this_link = link.get('href')

            if this_link[len(this_link) - 3:] == 'txt':
                link_ext = this_link
                break

        if link_ext == '':
            main_process()
            quit()

        # Open txt file url
        txt_url = f"https://www.gutenberg.org/files/{book_num}/{link_ext}"
        txt_r = requests.get(txt_url, stream=True)

        txt_r.encoding = "utf-8"

        # Check to see if the book contains a header and/or footer
        contains_header = False
        contains_footer = False
        if txt_r.text.__contains__("START OF THIS PROJECT"):
            contains_header = True
        if txt_r.text.__contains__("END OF THIS PROJECT"):
            contains_footer = True

        content = True
        if contains_header:
            content = False

        bag_o_words = {}
        title = "(Title Not Given)"

        # Run through the book to add words to bag of words based off of frequency
        try:
            for element in txt_r.iter_lines():
                this_str = str(element.decode())
                final_str = ""
                # Grab title for final output
                if this_str.startswith("Title:"):
                    title = this_str[this_str.index(":") + 2:]
                if contains_header:
                    if this_str.__contains__("START OF THIS PROJECT"):
                        contains_header = False
                        content = True
                        continue
                if contains_footer:
                    if this_str.__contains__("END OF THIS PROJECT"):
                        break
                if content:
                    for character in this_str:
                        if character.isalpha() or character == " ":
                            final_str += character.lower()

                    # Create smaller bag of words for this iteration
                    wallet_of_words = final_str.split(' ')
                    for word in wallet_of_words:
                        if word not in stop_words and word != "":
                            if word in bag_o_words:
                                bag_o_words[word] += 1
                            else:
                                bag_o_words[word] = 1
        except:
            main_process()      # Fool-proof method of ensuring code works every time
            quit()

        # Create sorted bag of words to make grabbing top 5 values easy
        sorted_bag = sorted(((value, key) for (key, value) in bag_o_words.items()), reverse=True)

        # Formatted output
        print(f"\nFor the book: {title}")
        time.sleep(1)
        print("The top 5 words were:\n")
        time.sleep(1)
        for i in sorted_bag[:5]:
            print(i[1], " and appeared ", i[0], " times.")
            time.sleep(1)

        print(txt_url)

    main_process()
    threading.Thread(target=main_process).start()
