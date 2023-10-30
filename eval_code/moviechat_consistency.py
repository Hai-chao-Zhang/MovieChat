"""
Adapted from: https://github.com/mbzuai-oryx/Video-ChatGPT/blob/main/quantitative_evaluation/evaluate_activitynet_qa.py
"""
import openai
import os
import re
import argparse
import json
import ast
import string


def parse_args():
    parser = argparse.ArgumentParser(description="question-answer-generation-using-gpt-3")
    parser.add_argument("--pred_path", required=True, help="The path to file containing prediction.")
    parser.add_argument("--output_dir", required=True, help="The path to save annotation json files.")
    parser.add_argument("--api_key", required=True, help="OpenAI API key.")
    args = parser.parse_args()
    return args

def check_sentence_start(sentence):
    sentence_lower = sentence.lower()

    if sentence_lower.startswith("does") or sentence_lower.startswith("do") or sentence_lower.startswith("is") or sentence_lower.startswith("are"):
        return True
    else:
        return False

def remove_punctuation(sentence):
    punctuation_set = set(string.punctuation)
    sentence_no_punct = ''.join(char for char in sentence if char not in punctuation_set)

    return sentence_no_punct

def main():
    """
    Main function to control the flow of the program.
    """
    # Parse arguments.
    args = parse_args()
    output_dir = args.output_dir

    pred_file = open(args.pred_path)
    pred_contents = json.load(pred_file)

    # Set the OpenAI API key.
    openai.api_key = args.api_key
    openai.api_base = "https://api.aiproxy.io/v1"

    # Preparing dictionary of question-answer sets
    prediction_set = {}
    pred_accuracy = []
    is_pred_accuracy = []
    pred_score = []
    is_pred_score = []
    for sample in pred_contents:
        id = sample.split(".")[0]
        qa_list = pred_contents[sample]
        for qa_pair in qa_list:
            question = qa_pair['question']
            answer = qa_pair['answer']
            pred = qa_pair['pred'].replace("</s>", "")
            qa_set = {"q": question, "a": answer, "pred": pred}
            prediction_set[id] = qa_set
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content":
                            "You are an intelligent chatbot designed for evaluating the contextual understanding of generative outputs for video-based question-answer pairs. "
                            "Your task is to compare the predicted answer with the correct answer and determine if the generated response aligns with the overall context of the video content. Here's how you can accomplish the task:"
                            "------"
                            "##INSTRUCTIONS: "
                            "- Evaluate whether the predicted answer aligns with the overall context of the video content. It should not provide information that is out of context or misaligned.\n"
                            "- The predicted answer must capture the main themes and sentiments of the video.\n"
                            "- Consider synonyms or paraphrases as valid matches.\n"
                            "- Provide your evaluation of the contextual understanding of the prediction compared to the answer."
                    },
                    {
                        "role": "user",
                        "content":
                            "Please evaluate the following video-based question-answer pair:\n\n"
                            f"Question: {question}\n"
                            f"Correct Answer: {answer}\n"
                            f"Predicted Answer: {pred}\n\n"
                            "Provide your evaluation only as a contextual understanding score where the contextual understanding score is an integer value between 0 and 5, with 5 indicating the highest level of contextual understanding. "
                            "Please generate the response in the form of a Python dictionary string with keys 'score', where its value is contextual understanding score in INTEGER, not STRING."
                            "DO NOT PROVIDE ANY OTHER OUTPUT TEXT OR EXPLANATION. Only provide the Python dictionary string. "
                            "For example, your response should look like this: {''score': 4.8}."
                    }
                ]
            )
            # Convert response to a Python dictionary.
            response_message = completion["choices"][0]["message"]["content"]
            # response_dict = ast.literal_eval(response_message)
            with open('consistency.txt', 'a') as file:
                file.write(response_message)
                file.write('\n')
     


if __name__ == "__main__":
    main()

    