class Output:
    def __init__(self, headers=[], content=[[]], /):
        self.headers = headers
        self.content = content

    @classmethod
    def create(cls, headers, group: {list}, key_index: int, /):
        tmp_content = [[]]
        for k in group.keys():
            # insert name in key index
            group[k][key_index] = k
            # add list to content
            tmp_content.append(group[k])


        return Output(headers, tmp_content)