def list_to_OR_string(input_list):
    i = 1
    n = len(input_list)
    if n == 0:
        # String to return if nothing is selected
        OR_string = 'XXXXXXX'
    else:
        OR_string = ''
        for word in input_list:
            if i == n:
                OR_string = OR_string + word

            elif i == 1:
                OR_string = word + '|'
                i += 1

            else:
                OR_string = OR_string + word + '|'
                i += 1

    return OR_string