from flask import jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

def submit_multi_step_zoho_form(url, file_paths, first_name, last_name, email, phone_number, wait_time=10):

    # Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(url)

    try:
        wait = WebDriverWait(driver, wait_time)
        i_am_ready = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="oneFieldSwiperSliderDiv"]/div[1]/div/div/div/div[3]/a')))
        i_am_ready.click()
        
        initial_steps = [
            {
                '//*[@id="Name-li"]/div[1]/div[2]/div[1]/div/div[1]/span/input': first_name,
                '//*[@id="Name-li"]/div[1]/div[2]/div[1]/div/div[2]/span/input': last_name,
            },
            {
                '//*[@id="Email-li"]/div[1]/div[2]/div[1]/span/input': email,
            },
        ]
        
        for step_index, step in enumerate(initial_steps):
            print(f"Filling out step {step_index + 1}...")
            for field_xpath, value in step.items():
                try:
                    # Wait for the input field to be present and interactable
                    input_field = wait.until(EC.element_to_be_clickable((By.XPATH, field_xpath)))
                    input_field.clear()
                    input_field.send_keys(value)
                    print(f"Entered '{value}' into field with XPath '{field_xpath}'.")
                except TimeoutException:
                    print(f"Timeout while waiting for field with XPath '{field_xpath}'.")
                    try:
                        # Wait for the input field to be present and interactable
                        input_field = wait.until(EC.element_to_be_clickable((By.XPATH, field_xpath)))
                        input_field.clear()
                        input_field.send_keys(value)
                        print(f"Entered '{value}' into field with XPath '{field_xpath}'.")
                    except TimeoutException:
                        print(f"Timeout while waiting for field with XPath '{field_xpath}'.")
                        try:
                            # Wait for the input field to be present and interactable
                            first_name_input = driver.find_element(By.CSS_SELECTOR, 'input[elname="First"]')
                            first_name_input.clear()
                            first_name_input.send_keys(value)
                            print(f"Entered '{value}' into field with XPath '{field_xpath}'.")
                        except TimeoutException:
                            print(f"Timeout while waiting for field with XPath '{field_xpath}'.")
                        
                except NoSuchElementException:
                    print(f"Could not find field with XPath '{field_xpath}'.")
                
                time.sleep(1)
                 
            # Click the "Next" button
            try:
                driver.execute_script("goNext()")
                time.sleep(2)
            except Exception as e:
                print(f"An error occurred: {e}")
                     
        # Check all input boxes
        input_boxes = [
            '//*[@id="Checkbox1-li"]/div[1]/div[2]/div[1]/div/span[1]/label',
            '//*[@id="Checkbox1-li"]/div[1]/div[2]/div[1]/div/span[2]/label',
            '//*[@id="Checkbox1-li"]/div[1]/div[2]/div[1]/div/span[3]/label',
            '//*[@id="Checkbox1-li"]/div[1]/div[2]/div[1]/div/span[4]/label',
            '//*[@id="Checkbox1-li"]/div[1]/div[2]/div[1]/div/span[5]/label',
            '//*[@id="Checkbox1-li"]/div[1]/div[2]/div[1]/div/span[6]/label',
            '//*[@id="Checkbox1-li"]/div[1]/div[2]/div[1]/div/span[7]/label',
            '//*[@id="Checkbox1-li"]/div[1]/div[2]/div[1]/div/span[8]/label',
        ]
            
        for box in input_boxes:
            try:
                input_field = driver.find_element(By.XPATH, box)
                input_field.click()
                print(f"Clicked '{box}' button.")
            except TimeoutException:
                print(f"Timeout while waiting for '{box}' button with XPath '{box}'.")
            except NoSuchElementException:
                print(f"Could not find '{box}' button with XPath '{box}'.")
                
            time.sleep(1)
                    
        # Click the "Next" button
        try:
            driver.execute_script("goNext()")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            
        try:
            # Click on the Select2 dropdown to open options
            dropdown = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "select2-selection--single")))
            dropdown.click()
            print("Clicked dropdown.")

            # Select the option with value "3"
            option_xpath = '//li[contains(@class, "select2-results__option") and text()="3"]'
            option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
            option.click()
            print("Selected option 3.")

        except Exception as e:
            print(f"Error: {e}")
            
        # Click the "Next" button
        try:
            driver.execute_script("goNext()")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            
        # Upload files
        try:
            # Locate the file upload input element
            file_input = driver.find_element(By.ID, "FileUpload2-id")

            # Join all file paths into a single string (separated by newlines)
            file_input.send_keys("\n".join(file_paths))

            print("Files uploaded successfully!")

            # Wait to see the upload preview (optional)
            time.sleep(15)

        except Exception as e:
            print(f"Error: {e}")
            
        # Click the "Next" button
        try:
            driver.execute_script("goNext()")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            
        # Fill out name
        try:
            input_field = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="SingleLine-li"]/div[1]/div[2]/div[1]/input')))
            input_field.clear()
            input_field.send_keys(first_name + ' ' + last_name)
            print(f"Entered '{first_name + ' ' + last_name}' into phone number field.")
        except TimeoutException:
            print(f"Timeout while waiting for phone number field.")
        except NoSuchElementException:
            print(f"Could not find phone number field.")
            
        # Click the "Next" button
        try:
            driver.execute_script("goNext()")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")
            
        # Accept terms
        try:
            label_xpath = '//label[@for="TermsConditions-input"]'
            label = driver.find_element(By.XPATH, label_xpath)
            label.click()
            print("Accepted Terms and Conditions.")
        except Exception as e:
            try:
                driver.execute_script("document.getElementById('TermsConditions-input').checked = true;")
                print("Accepted Terms and Conditions.")
            except Exception as e:
                print(f"Error: {e}")
                
        # Click the "Next" button
        try:
            driver.execute_script("goNext()")
            time.sleep(2)
        except Exception as e:
            print(f"An error occurred: {e}")

        # Fill out phone number
        try:
            # Locate the phone number input field
            phone_input_xpath = '//input[@id="PhoneNumber"]'
            phone_input = wait.until(EC.presence_of_element_located((By.XPATH, phone_input_xpath)))
            phone_input.clear()
            phone_input.send_keys(phone_number)

            print("Phone number entered successfully!")

            # Wait to see the result
            time.sleep(3)
        except Exception as e:
            print(f"Error: {e}")
            
            
        
        # Click the "Submit" button
        try: 
            driver.execute_script("goNext()")
            submit = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="navFooter"]/div[3]/button')))
            submit.click()
            print("Clicked Submit button.")
        except Exception as e:
            try:
                # Wait for the form to load (adjust timeout as needed)
                wait = WebDriverWait(driver, 10)
                try:
                    wait.until(EC.presence_of_element_located((By.XPATH, '//button[@elname="submit"]')))
                    print("Next step loaded.")
                    submit_button_xpath = '//button[@elname="submit"]'
                    submit_button = driver.find_element(By.XPATH, submit_button_xpath)
                    driver.execute_script("arguments[0].click();", submit_button)
                except:
                    print("Next step did not load in time.")
                    next_button_xpath = '//a[@class="flRight zf-next"]'
                    # Make button visible
                    driver.execute_script("document.querySelector('.zf-next').style.display = 'inline-block';")
                    # Click the button
                    next_button = driver.find_element(By.XPATH, next_button_xpath)
                    driver.execute_script("arguments[0].click();", next_button)
                    print("Next button clicked after making it visible.")
            except Exception as e:
                print(f"An error occurred: {e}")
        
        time.sleep(15)
        
        print("Form submitted successfully!")
        return jsonify({"status": "success"})
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "fail", "error": e})

    finally:
        driver.quit()
