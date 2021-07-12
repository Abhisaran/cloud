# s1 = input("Enter the string")
# l = []
# for i in range(len(s1)):
#     if s1[i] == ' ':
#         l.append(s1[i])
#     if s1[i] == 'a' or s1[i] == 'e' or s1[i] == 'i' or s1[i] == 'o' or s1[i] == 'u':
#         l.append('+')
#     else:
#         l.append('-')
# print("Hangman game:")
# count = len(s1)
# while count > 0:
#     print("Word to guess:")
#     s2 = ""
#     for i in range(len(l)):
#         s2 = s2 + l[i]
#     print(s2)
#     option = input("Enter the letter to guess:")
#     if option in s1:
#         for i in range(len(s1)):
#             if s1[i] == option:
#                 l[i] = option
#     else:
#         print("Wrong guess!")
#         count = count - 1
#     if '+' not in l and '-' not in l:
#         print("Success you guessed the word!")
#         count = 0
#
# if '+' in l or '-' in l:
#     print("Sorry game over")
# print("Word to be guessed is:")
# print(s1)]

def calculate_frequencies(file_contents):
    # Here is a list of punctuations and uninteresting words you can use to process your text
    punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    uninteresting_words = ["the", "a", "to", "if", "is", "it", "of", "and", "or", "an", "as", "i", "me", "my", \
                           "we", "our", "ours", "you", "your", "yours", "he", "she", "him", "his", "her",
                           "hers", "its", "they", "them", \
                           "their", "what", "which", "who", "whom", "this", "that", "am", "are", "was",
                           "were", "be", "been", "being", \
                           "have", "has", "had", "do", "does", "did", "but", "at", "by", "with", "from",
                           "here", "when", "where", "how", \
                           "all", "any", "both", "each", "few", "more", "some", "such", "no", "nor", "too",
                           "very", "can", "will", "just"]

    # LEARNER CODE START HERE
    frequencies = {}
    words = file_contents.split()
    words = [x for x in words if x not in uninteresting_words]
    for i in words:
        # print(i)
        i1 = i.lower().strip(punctuations)
        # print(i1)
        if not i1 or not i1.isalpha() or i1 in uninteresting_words or len(i1)<=3:
            continue
        if i1 in frequencies:
            frequencies[i1] += 1
        else:
            frequencies[i1] = 1
    # wordcloud

    return frequencies


with open('test.txt', 'r',encoding="utf8") as file:
    data = file.read()
# print(calculate_frequencies(data))

dic = calculate_frequencies(data)
for i in dic:
    # if int(dic[i]) > 6:
    print(i + ': ' + str(dic[i]))