def countAndSay(n):
    if n == 1:
        return "1"
    prev = countAndSay(n - 1)
    result = []
    i = 0
    while i < len(prev):
        current_char = prev[i]
        count = 1
        while i + 1 < len(prev) and prev[i + 1] == current_char:
            count += 1
            i += 1
        result.append(str(count))
        result.append(current_char)
        i += 1
    
    return ''.join(result)


print(countAndSay(5))