from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import torch
import torch.nn.functional as F


class QAGenerator:
    model = None
    tokenizer = None

    def __init__(self, model, tokenizer, link):
        self.model = model
        self.tokenizer = tokenizer
        self.link = link

    def search_geeks_for_geeks(self, question):
        content = ""
        driver = webdriver.Chrome()
        driver.get(self.link)
        try:
            wait = WebDriverWait(driver, 10)

            # Find and click the search icon
            search_icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "gcse-search__btn")))
            search_icon.click()

            # Find the search input, clear it, and type the question
            search_input = wait.until(EC.element_to_be_clickable((By.ID, "gcse-search-input")))
            search_input.clear()
            search_input.send_keys(question)
            search_input.send_keys(Keys.RETURN)

            # Wait for the results to appear
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "gcse-results-wrapper")))

            # Find the first result and click on it
            first_result = driver.find_element(By.CSS_SELECTOR, ".gcse-title a")
            first_result.click()

            # Wait for the article content to load
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Get the article content
            content = driver.find_element(By.CLASS_NAME, "article--viewer").text

        except Exception as e:
            print("An error occurred:", e)

        finally:
            driver.close()
            return content

    def answer(self, question, text):
        answer = ""
        input_ids = self.tokenizer.encode(question, text)
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids)
        sep_idx = input_ids.index(self.tokenizer.sep_token_id)

        num_seg_a = sep_idx + 1
        num_seg_b = len(input_ids) - num_seg_a
        segment_ids = [0] * num_seg_a + [1] * num_seg_b
        assert len(segment_ids) == len(input_ids)

        output = self.model(torch.tensor([input_ids]), token_type_ids=torch.tensor([segment_ids]))

        start_logits = output.start_logits
        end_logits = output.end_logits

        start_probs = F.softmax(start_logits, dim=1)
        end_probs = F.softmax(end_logits, dim=1)

        answer_start = torch.argmax(start_logits)
        answer_end = torch.argmax(end_logits)

        # Get the probability of the start and end positions
        start_prob = start_probs[0, answer_start].item()
        end_prob = end_probs[0, answer_end].item()

        # Calculate the overall confidence score
        confidence = start_prob * end_prob

        if answer_end >= answer_start:
            answer = tokens[answer_start]
            for i in range(answer_start + 1, answer_end + 1):
                if tokens[i][0:2] == "##":
                    answer += tokens[i][2:]
                else:
                    answer += " " + tokens[i]

        if answer.startswith("[CLS]"):
            answer = "Unable to find the answer to your question."

        return answer.capitalize(), confidence

    def generate(self, question):
        confidence = 0.0
        text = self.search_geeks_for_geeks(question)
        answer = None
        end_points = [i for i in range(0, len(text), 200)]
        n = 0
        while confidence < 0.90 and n < len(end_points) - 1:
            tmp_answer, confidence = self.answer(question, text[end_points[n]:end_points[n + 1]])
            if confidence >= 0.6:
                answer = tmp_answer
                break
            n += 1
        return answer
