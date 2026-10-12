对论文的切分，只是粗略地把整个文章进行字数的切分，还加了一个句子之间重叠的考虑。这样切分出来的效果比较差，文档怎么切分也很重要。对于论文这种切分，。刚好md文档，那么最好是按照文章中的段落章节进行切分。章节太长了的话，再按照1000字继续切分。

`chunk` 是概念，`Document` 是 LangChain 里承载这段文本的数据结构。

Document(
    page_content="第一个 chunk 的内容",
    metadata={"source": "xxx.md"}
)

Document(
    page_content="第二个 chunk 的内容",
    metadata={"source": "xxx.md"}
)
