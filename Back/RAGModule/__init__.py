from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from utils import *


# class Chain4RAG:
#     def __init__(self, model):
#         ## 你将作为协助用户围绕调研场景Scenario进行信息调研的助手。请从SentenceList中为IntentsDict中的每一对Intent和Description各自筛选最多k个最相关的句子，并返回这些句子在SentenceList中的相应索性作为top-k。
#         self.instruction = """
# # System
#     你将作为协助用户围绕调研场景Scenario进行信息调研的助手，筛选出与每个意图Intent和对应描述Description足够相关的所有句子，如果没有足够相关的句子符合条件，可能返回0个，并按照相似度从高到低的顺序返回这些句子在SentenceList中的索引位置。

# # Steps
# 1. **理解输入结构**：
#    - **Scenario**: 调研场景。
#    - **SentenceList**: 一个包含多个句子的列表。
#    - **IntentsDict**: 结构为{{intent: description}}

# 2. **筛选并匹配**：
#    - 针对IntentsDict中的每一对Intent和Description，分析其内容以确定其主题。
#    - 分析SentenceList中的句子，理解其内容，判断是否属于当前Intent和Description的主题。
#    - 筛选出属于主题的所有句子，但如果没有句子满足条件，可以返回0个。
   
# 3. **收集结果**：
#    - 将筛选出的句子在SentenceList中的索引位置作为结果返回，按照相似度从高到低的顺序排列。
#    - 如果没有筛选出符合条件的句子，则topKIndices返回空列表

# # Output Format
#     结果以Json形式输出，其中每个元素是一个字典，字典包含两个键：
#     - {format_instructions}

# # User:
#     Scenario: {scenario}
#     IntentsDict: {intentsDict}
#     SentenceList: {sentenceList}
#     top_threshold: {top_threshold}
# """
# #         self.instruction = """
# # ## System
# # 你将作为协助用户围绕调研场景Scenario进行信息调研的助手。请基于Description从SentenceList中筛选最多k个最符合Intent的句子，并返回这些句子在SentenceList中的相应索引作为top-k。此外，根据RecordList，挑选出符合Intent的前提下最能提供新信息的k个句子，并返回这些句子在SentenceList中的相应索引作为bottom_k。
# # # Steps
# # 1. **理解场景和Intent和Description**：
# #     - 如果Description为空字符串，根据Scenario和Intent进行推理，补全Description。
# #     - 仔细阅读给定的场景和Description以理解Intent是什么，目标是理解用户需要哪些信息。
# # 2. **筛选top_k句子**：
# #    - 分析SentenceList中的每个句子，并评估其是否属于用户需要的信息。
# #    - 选择用户最需要的k个句子。
# #    - 记录这些句子在SentenceList中的索引，将其标识为top_k。
# #    - 仅当句子与Intent高度相关时才选择，如果没有满足条件的句子则不选择。
# # 3. **筛选bottom_k句子**：
# #    - 分析RecordList中的内容。
# #    - 评估top_k中筛选出的哪些句子的内容与RecordList中的内容存在明显差异。
# #    - 选择最能提供新信息的k个句子。
# #    - 记录这些句子在SentenceList中的索引，将其标识为bottom_k。
# #    - 仅当句子与Intent高度相关时才选择，如果没有满足条件的句子则不选择。

# # # Output Format
# #     - 输出格式为JSON，包含两个字段：
# #     - {format_instructions}

# # # Notes
# # - 评选top_k时，首先要考虑是否属于用户需要的信息，如果没有满足条件的句子则不筛选。
# # - 评选bottom_k时，同样首先要考虑是否属于用户需要的信息，如果没有满足条件的句子则不筛选。
# # - 如果RecordList不为空列表，正常返回结果。
# # - 如果RecordList为空列表,将标识为top_k的句子标识为bottom_k返回，并且top_k在此时返回空列表，否则。
# # - 比较top_k和bottom_k的索引，去除top_k中与bottom_k重复的索引。

# # ## User:
# #     Scenario: {scenario}
# #     Intent: {intent}
# #     Description: {description}
# #     SentenceList: {sentenceList}
# #     RecordList: {recordList}
# #     k: {k}
# # """

#         self.model = model
#         # self.parser = JsonOutputParser(pydantic_object=sentenceGroupsIndex)
#         self.parser = JsonOutputParser(pydantic_object=TopKIndexList)
#         self.prompt_template = PromptTemplate(
#             # input_variables=["scenario", "intentList", "recordList", "sentenceList", "k", "description"],
#             input_variables=["scenario", "intentsDict", "sentenceList", "top_threshold"],
#             template=self.instruction,
#             partial_variables={
#                 "format_instructions": self.parser.get_format_instructions()
#             },
#         )

#         self.chain = self.prompt_template | self.model | self.parser

#     async def invoke(self, scenario, intentsDict, sentenceList, top_threshold):
#         return self.chain.invoke(
#             # {"scenario": scenario, "intent": intent, "sentenceList": sentenceList, "recordList": recordList, "k": k, "description": description}
#             {"scenario": scenario, "intentsDict": intentsDict, "sentenceList": sentenceList, "top_threshold": top_threshold}
#         )
    
class Chain4RAG:
    def __init__(self, model):
        ## 你将作为协助用户围绕调研场景Scenario进行信息调研的助手。请从SentenceList中为IntentsDict中的每一对Intent和Description各自筛选最多k个最相关的句子，并返回这些句子在SentenceList中的相应索性作为top-k。
        self.instruction = """
## System  
You are tasked with assisting the user in conducting information research based on a specified scenario. Your goal is to filter sentences from a given `SentenceList` for each Intent provided in the `IntentsDict`. Ensure all indices in the output start from 0 and do not exceed the length of `SentenceList`.

### Steps  
1. **Understand Input Structure:**  
   - **Scenario**: Describes the context for the research.  
   - **SentenceList**: A list of sentences, indexed starting from 0. 
   - SentenceList contains `N` sentences, where `N = len(SentenceList)`. Ensure all indices are strictly within `[0, N-1]`.
   - **IntentsDict**: A dictionary structured as `{{"intent": "description"}}`, where the description provides a summary of the theme and any existing sub-themes.  

2. **Filter and Match:**  
   For each `Intent` and `Description` in `IntentsDict`:  
   - **Theme Analysis**: If `Description` is empty, infer the theme based on the `Scenario` and `Intent` and complete the `Description`.  
   - **Sentence Evaluation**: For each sentence in `SentenceList`:  
     - Determine if the sentence aligns with the theme of the Intent and any existing sub-themes:  
       - If aligned with **both**, add the sentence's index to `top_all[Intent]`.  
       - If aligned with only the **theme** (not with sub-themes, or if no sub-themes are specified), add the sentence's index to `bottom_all[Intent]`.  
   - If no sentences match the criteria, return an empty list for `top_all[Intent]` or `bottom_all[Intent]` as applicable.  

### Output Format  
- The output should be a dictionary with two main keys: `top_all` and `bottom_all`.
  - {format_instructions}
  - `top_all`: Maps to a dictionary where each Intent key contains a list of indices corresponding to sentences aligned with both the theme and sub-themes.  
  - `bottom_all`: Maps to a dictionary where each Intent key contains a list of indices corresponding to sentences aligned with only the theme (but not sub-themes).  
- Example output:  
  ```json
  {{
    "top_all": {{
      "intent1": [0, 2, 3],
      "intent2": []
    }},
    "bottom_all": {{
      "intent1": [10],
      "intent2": [24, 27, 30]
    }}
  }}
  ```

### Notes  
- Ensure **all indices in the output start from 0 and are strictly less than the length of `SentenceList`**.  
- Pay attention to the distinction between themes and sub-themes to classify sentences accurately.  
- Provide a comprehensive and accurate `Description` to ensure correct filtering.  
- Include sentences in the appropriate lists only if they fully meet the criteria for alignment.  

## User:
    Scenario: {scenario}
    IntentsDict: {intentsDict}
    SentenceList: {sentenceList}
"""

        self.model = model
        self.parser = JsonOutputParser(pydantic_object=sentenceGroupsIndex)
        # self.parser = JsonOutputParser(pydantic_object=RAGIndexList)
        self.prompt_template = PromptTemplate(
            # input_variables=["scenario", "intentList", "recordList", "sentenceList", "k", "description"],
            input_variables=["scenario", "intentsDict", "sentenceList"],
            template=self.instruction,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        self.chain = self.prompt_template | self.model | self.parser

    async def invoke(self, scenario, intentsDict, sentenceList):
        return self.chain.invoke(
            # {"scenario": scenario, "intent": intent, "sentenceList": sentenceList, "recordList": recordList, "k": k, "description": description}
            {"scenario": scenario, "intentsDict": intentsDict, "sentenceList": sentenceList}
        )

class Chain4Split:
    def __init__(self, model):
        ## 你将作为协助用户围绕调研场景Scenario进行信息调研的助手。请将WebContent按上下文语义分句，过滤掉无意义的乱码内容，并以列表形式返回。
        self.instruction = """
## System
Segment web content into sentences by semantic context, eliminating meaningless gibberish, and return as a list.

### Steps
    1. **内容分句**: 结合上下文的语义，对Web内容进行分句处理。
    2. **过滤乱码**: 识别并移除无意义或乱码的部分，确保仅返回有意义的信息。
    3. **格式化输出**: 将分句后的有效内容以列表格式呈现。

### Output Format
    - 以条目列表的形式提供，每个条目为一完整有意义的句子。
    - {format_instructions}

### Notes
    - 注意识别乱码可能因不同语言或编码格式而异。
    - 确保所有重要信息得以保留，而不仅仅是去除明显的乱码。

## User:
    Scenario: {scenario}
    WebContent: {webContent}
"""

        self.model = model
        self.parser = JsonOutputParser(pydantic_object=SplitContent)
        self.prompt_template = PromptTemplate(
            input_variables=["scenario", "webContent"],
            template=self.instruction,
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )

        self.chain = self.prompt_template | self.model | self.parser
    
    async def invoke(self, scenario, webContent):
        return self.chain.invoke(
            {"scenario": scenario, "webContent": webContent}
        )