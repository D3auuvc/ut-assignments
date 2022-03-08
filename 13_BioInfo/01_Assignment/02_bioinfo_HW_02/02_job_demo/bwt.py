btw_str = 'ACTCA$TA'


words = list(btw_str)
list = {}
# Rotate the string
for i in range(len(words)):
    word = btw_str[-1] + btw_str[:-1]
    new = ''.join(word)
    btw_str = new
    list[i] = new
    i += 1

print('==='*10)
print('Rotate the string:')
for key, value in list.items():
    print(key, value)

# Sorted the rows alphabetically
sort = {k: v for k, v in sorted(list.items(), key=lambda x: x[1])}
print('==='*10)
print('Sorted the rows alphabetically:')
for key, value in sort.items():
    print(key, value)

print('==='*10)
print('Extract the characters of the last columns only:')
# Extract the characters of the last columns only
for i in range(len(words)):
    element = sort[i]
    last = element[- 1]
    i = i + 1
    print(last)
