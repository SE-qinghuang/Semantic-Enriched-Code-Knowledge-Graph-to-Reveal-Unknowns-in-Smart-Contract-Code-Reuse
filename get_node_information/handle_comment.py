import re


# if there is comment with the pattern of '/* ...*/
def get_format_comment_with_pattern1(comment):
    # avoid the web string like : https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    comment = comment.replace('/*', '')
    comment = comment.replace('*/', '')
    comment = comment.replace('*', '')

    list_of_comment = comment.split('\n')
    # comment = get_format_comment(list_of_comment)
    format_have_done = False

    while (format_have_done == False):
        a = len(list_of_comment)

        list_have_changed = False

        for i in range(len(list_of_comment)):
            now_comment = list_of_comment[i].strip()
            if len(now_comment) == 0:
                list_of_comment.pop(i)
                list_have_changed = True
                break

            # if the end is .,the sentence is end.
            if now_comment[-1] == '.':
                list_of_comment[i] = now_comment + '\n'
                continue

            elif now_comment[-1] == ':':
                if (i + 1) >= len(list_of_comment):
                    list_of_comment[i] = now_comment
                else:
                    next_comment = list_of_comment[i + 1].strip()
                    list_of_comment[i] = now_comment + ' ' + next_comment
                    list_of_comment.pop(i + 1)
                    list_have_changed = True
                    break
            else:
                # if there is no '.' at the end,but no element exist in i+1 index
                if (i + 1) >= len(list_of_comment):
                    list_of_comment[i] = now_comment + '.\n'

                else:

                    # If the next word starts in lowercase
                    next_comment = list_of_comment[i + 1].strip()
                    if len(next_comment) == 0:
                        list_of_comment.pop(i + 1)
                        list_have_changed = True
                        break
                    if next_comment[0].islower():
                        list_of_comment[i] = now_comment + ' ' + next_comment
                        list_of_comment.pop(i + 1)
                        list_have_changed = True
                        break
                    else:
                        list_of_comment[i] = now_comment + '.\n'
        if list_have_changed:
            continue
        else:
            if i == len(list_of_comment) - 1:
                format_have_done = True

    format_comment = ''
    for element in list_of_comment:
        format_comment += element
    return format_comment


# if there is comment with the pattern of '//' or '///'
def get_format_comment_with_pattern2(comment):
    # comment = comment.replace('///', '')
    # comment = comment.replace('//','')
    comment = re.sub('/{2,}', '', comment)
    comment_list = comment.split('\n')
    format_have_done = False
    while (format_have_done == False):
        for i in range(len(comment_list)):
            now_comment = comment_list[i].strip()
            if len(now_comment) == 0:
                comment_list.pop(i)
                break

            if now_comment[-1] == '.':
                comment_list[i] = now_comment + '\n'
                continue
            else:
                comment_list[i] = now_comment + '.\n'
        if i == len(comment_list) - 1:
            format_have_done = True
    format_comment = ''
    for element in comment_list:
        format_comment += element
    return format_comment


def format_the_comment(comment):
    if ('/*' in comment) & ('*/' in comment):

        format_comment = get_format_comment_with_pattern1(comment)
    elif ('//' in comment) | ('///' in comment):
        format_comment = get_format_comment_with_pattern2(comment)
    else:
        if len(comment.strip()) == 0:
            format_comment = 'no comment'
        elif comment == 'no comment':
            format_comment = 'no comment'
        else:
            format_comment = "haven't find the pattern"

    return format_comment
