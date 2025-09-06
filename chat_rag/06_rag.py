import os

abs_path = os.path.abspath(__file__)
print({"abs_path": abs_path})
current_path = os.path.dirname(abs_path)
print({"current_path": current_path})
print(os.listdir("."))
book_dir = os.path.join(current_path, "books")
print({"book_dir": book_dir})
print({"all_book_dir": os.listdir(book_dir)})

all_book = [bk for bk in os.listdir(book_dir) if bk.endswith('.txt')]
# print({"all_book": all_book})

for bkf in all_book:
    print(bkf)
