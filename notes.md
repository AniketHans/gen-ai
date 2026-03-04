# Generative AI

## GPT

1. GPT stands for Generative Pre-Trained Transformer
   1. It is used simply to generate transformations for an input to a output based on the pre trained data or pre-trained conversions.
      1. Generative means to generate/create something
      2. Transformer means transforming an input to some output like converting/translating english input into hindi
      3. Pre-trained model on some data is used in this process
   2. Here, we use some neural networks that are trained on some data where we have some input and some output. The NN is fined tuned on the data and then it is used to convert new inputs into output based on the previously trained data
   3. GPT transformers are trained to predict the next word based on the input word sequence. They keep on predicting data until end of the sentence is not reached or full context of the input is not matched. The prediction is done on the pretrained data
      !["GPT Transformer"](./images/01.gpt.png)
2. Process of converting the input into output by GPT:
   1. Tokenization:
      1. The input sentence is divided into tokens
      2. The tokenization depends on model to model.
      3. The model divides the sentence into words that match with words present in their vocab
         1. Eg: gpt 4o converts the sentence "Hey whats up" into tokens: [25216, 55993, 869]
      4. Each token in the model vocab has a number associated with it. The same words will get same number
      5. The flow is: sentence --> vocab words --> numbers (tokens)
   2. Vector Embeddings
      1. A vector embedding is a list of numbers that represents the meaning of something (text, image, audio).
      2. Computers don’t understand meaning directly, but they are good with numbers. Embeddings convert things like words, sentences, images into numbers in such a way that similar things get similar numbers.
      3. Every word/sentence gets coordinates in a meaning-space, Similar meanings → close together, Different meanings → far apart
      4. Example with sentences:
         1. “I love dogs” and “Dogs are my favorite animals”. Their embeddings are very close
         2. “I love dogs” and “My car needs fuel”. Their embeddings are far apart
      5. The vector space is multidimensional and the vector embeddings provide the relative position of the input sentence in that space based on the similarities with other sentences. Each number in vector embedding is between -1 and 1, where -1 means opposite meaning, 0 means unrelated and 1 means very similar
      6. If 2 sentence have vector embeddings close to each other then it means they are similar
      7. Vector embeddings are numeric representations of meaning, where similar things are close together in a multi-dimensional space.
   3. Positional Encodings:
      1. It is just the vector encodings of a word/sentence along with its sequence number in the the given input.
      2. This is important so vector embeddings of 2 sentences like "cat like dog" and "dog like cat" does not came to be same as both the sentences have different meanings
   4. Attention:
      1. The Positional embeddings are then used to create multi head attentions
      2. Attention lets each word decide which other words matter most to it.
         1. Eg: “The animal didn’t cross the street because it was tired.” What does “it” refer to?. Attention helps the model figure that out.
      3. Single-head attention
         1. The model has one attention mechanism
         2. Each word looks at other words in one single
         3. Eg: “I went to the bank to deposit money” . Single-head attention might focus mainly on: “bank” ↔ “money”. But it can miss other relationships.
         4. Pros and cons
            1. ✅ Simple
            2. ❌ Limited perspective
            3. ❌ One focus only
         5. `Word → [Attention] → Context`
      4. Multi-head attention
         1. Instead of one attention, we have many heads.
         2. Each head learns to focus on different relationships
         3. Common transformer models use:
            1. 8 heads
            2. 12 heads
            3. 16 heads
         4. Eg: “The cat sat on the mat because it was soft.”
            1. Different heads might focus on:
               1. Head 1 → “it” ↔ “mat” (meaning)
               2. Head 2 → “cat” ↔ “sat” (grammar)
               3. Head 3 → “because” ↔ cause/effect
            2. Single-head attention can only do one of these
         5. ```
                Word → [Head1]
                     → [Head2]
                     → [Head3]
                     → Combine → Context
            ```
   5. Learning:
      1. During training, a Transformer learns by repeatedly:
         1. Taking an input sentence
         2. Using multi-head self-attention to decide which words should influence each other
         3. Making a prediction (next word, masked word, translation, etc.)
         4. Measuring error
         5. Updating attention weights so future predictions improve
      2. Multi-head attention is the core mechanism that lets the model learn relationships in the data.

## Prompting

1. We provide input tokens to the LLM and they generate the output based on those tokens. Thus, the quality of input tokens used plays a very important in determining the quality of the output.
2. The prompt is the input text you give to the model. The text is then broken down into token by the model's tokenizer
3. The more richer the prompt the more accurate the result
4. Prompting Styles
   1. Alpaca prompt

      ```
        ### Instruction:
        Explain the following concept in simple terms.

        ### Input:
        Database index

        ### Response:

      ```

   2. ChatML (current Industry Standard)

      ```
        <|system|>
        You are a database expert who explains things simply.

        <|user|>
        Explain what a database index is.

        <|assistant|>

      ```

   3. INST Format

      ```
        <<SYS>>
        You are a helpful assistant.
        <</SYS>>

        [INST] Explain what a database index is in simple terms. [/INST]
      ```

5. Different LLMs accept prompts in different prompt styles but in current market, ChatML is used and almost LLMs accept it and convert the ChatML format prompts to the desired style if needed.
6. We provide some system prompts to the models to restrict their area of output. Like we create an AI agent for mathematics that should not perform any other operations, otherwise it will be like chatting with ChatGPT or other models which are ready to any output for any query
7. The chats will the models are stateless. It means suppose you have an API call with the LLM agent stating your name, then in next call if you again send the question like "who am I?", the LLM will not be able to answer it. To chat continously and multiple times, you need to send the previous full chat context (containing both the previous user inputs and LLM outputs) along with the new chat so the LLM is aware of the context of the full chat.
   1. If the chat goes very huge, say 400 msgs (from both user input and llm output), then may be you can summarize the older 300 messages using AI agent and then send the new messages with the summary.
8. Type of Prompting:
   1. Zero shot prompting
      1. You ask an AI to do a task without giving it any examples first.
   2. Few shots prompting
      1. You show the AI a few examples of a task, then ask it to do the same for a new input.
   3. Chain of thoughts prompting
      1. You ask the AI to think step by step before giving the final answer.
   4. Self consitency prompting
      1. Here, we generate answers from multiple agents and then feed them to another agent asking it to return the most common answer as result
   5. Persona based prompting
      1. Here, we ask the model to answer by personification someone. You just provide the model with some example of may be chats, video transcript etc related to the person you want the model to personify and then ask it output the result in same way the person would have given it

## Agents / Agentic AI

1. The LLMs are trained at some intervals of time. They always lack some latest and rapidly changing info like current time, weather of a place etc.
2. Also, LLMs are just models trained on some data and they just give the output on some input based on the training they have done.
3. LLMs dont have internet access on their own but we can provide them with internet access by using/building some external tools.
4. The LLMs along with access to external tools in known as an Agent

## RAG

1. RAG stands for Retrieval Augumented Generation
2. Suppose you have some company data and you want the LLM to respond to user based on that data. There are 2 possible ways:
   1. Train the model based on your data
      1. Training a model is very time and resource consuming process.
      2. Also if your organization has continously changing data, then the model will always be lagging behind data changes
   2. Feed the data in context so the model can respond based on that
      1. This is possible as we feed the data in context so the model can pick necessary info from it and share it with the user.
      2. But the challenge is that the data can be huge in size, so if we try to send the full data in the context then it will hit the token limit and increase the costing a lot
      3. To resolve this issue, we use RAGs
3. In RAG, we first ingest our data into a vector database along with the data they represent. Then, when user query some info, we first fetch the relevant vectors from the vector database along with the data we then we add the data and the user query to the LLM and the LLM answers the user based on the context
4. In RAG, we have the following 2 phases:
   1. Ingestion
      1. Suppose, you have your company data in some format say PDF. The PDF size can be huge.
      2. Here, we first parse the PDF using some tools available in market. Langchain tools are popular in the market.
      3. Then, we divide the PDF parsed data into chunks. The chunks can be made per page or they can be made with some charcter limit say 1000 characters
      4. Then, we create vector embeddings for each chunk. The vector embeddings will also have the chunk text as metadata so that we can fetch the data when we are fetching some chunk
      5. Then, we store the generated vector embeddings in some vector database.
   2. Retrieval
      1. When user queries some data, we first create vector embeddings of the user query.
      2. Then, we search the vector database and fetch related vector embeddings with the user query vector embeddings
      3. The fetched vector embeddings will have metadata, containing the actual company data chunks, with them. We then put that metadata from each fetched vector embedding into the SYSTEM_PROMPT and also add the user query along with it.
      4. The LLM will provide the answer to the user query based on the system prompt containing the company data.
         ![Rag](./images/02.rag.png)
