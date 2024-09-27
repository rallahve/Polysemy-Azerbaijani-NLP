# Polysemy-Azerbaijani-NLP

## **Abstract**

This project implies the challenging task of Natural Language Processing (NLP) in low-resource languages such as Azerbaijani despite having an average of 25 million speakers worldwide. The paper focuses on different language models differentiating a list of Azerbaijani polysemous words according to their meanings in context. Experimenting clusters with K-Means, the project focuses on the accuracy of three different models: XL-LEXEME, XLM-RoBERTa, BERT- TURKISH. Ultimately being chosen as the most promising model, XL_LEXEME performed an average of 0.61 F1 score and 0.62 accuracy score. This was carried out on 60 polysemous words from online Azerbaijani polysemous words dictionary and 4326 sentences from online Azerbaijani language corpus, “azcorpus”. For the endeavours in future, this project will serve for transfer learning to be further refined, providing annotated phrases, a candidate list of polysemous words, integrated model, editable code, and other valuable insights regarding the NLP problem of other widely spoken but low-resource languages like Azerbaijani.

## **File Descriptions**

* _"qmul_final_project.ipynb"_ - Main project to be run. Available as both .py and .ipynb file.
* _"top_60_nouns.csv"_ - Candidate list of polysemous Azerbaijani words.
* _"60words_annotated.csv"_ - Candiadte list of sentences to be plotted by the models.
* _"f1_accuracy.csv"_ - F1 and Accuracy scores of the XL-LEXEME model.
* _"functions.py" and "requirements.txt"_ - XL-LEXEME plotting functions and dependencies. 
