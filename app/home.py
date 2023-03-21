import requests
import streamlit as st


def main():
    st.set_page_config(layout='wide')
    st.title('Nutrition Bot')
    st.markdown('Ask any nutrition-related question and you\'ll get answers from both scientific research papers and social media')

    with st.form(key='my_form'):
        query = st.text_input('Enter your query:') # Input text box
        submit = st.form_submit_button('Ask!') # Submit button

    if submit and query is not None:

        response = requests.get('http://35.207.46.114:8060/search/'+query) # API endpoint for nutritionbot
        response_json = response.json() # Get json from response
        ans_respp = response_json['research_paper_results']
        ans_socmed = response_json['reddit_results']

        respp, socmed = st.columns([2, 1])

        with respp: # One column for answers from research paper
            st.subheader("Research Papers") 
            for ans in ans_respp:
                ans_index_start = ans['content'].find(ans['answer'])
                ans_index_end = ans_index_start + len(ans['answer'])
                st.markdown(ans['content'][:ans_index_start] + "**<span style='color:#02f53f'>" + ans['content'][ans_index_start:ans_index_end] + "</span>**" + ans['content'][ans_index_end:], unsafe_allow_html=True) # Answer highlighted in color
                st.write(f'Score: **{ans["score_y"]:.3f}**') # Confidence score
                st.write(f'Source: {ans["doi_link"]}') # Link to research paper
                st.markdown("---")

        with socmed: # One column for answers from social media (reddit)
            st.subheader("Social Media")
            for ans in ans_socmed:
                ans_index_start = ans['content'].find(ans['answer'])
                ans_index_end = ans_index_start + len(ans['answer'])
                st.markdown(ans['content'][:ans_index_start] + "**<span style='color:#02f53f'>" + ans['content'][ans_index_start:ans_index_end] + "</span>**" + ans['content'][ans_index_end:], unsafe_allow_html=True) # Answer highlighted in color
                st.write(f'Score: **{ans["score_y"]:.3f}**') # Confidence score
                st.write(f'Source: {ans["thread_link"]}') # Link to reddit post
                st.markdown("---")


if __name__ == '__main__':
    main()