import requests
import streamlit as st


def main():
    st.set_page_config(layout='wide')
    st.title('Nutrition Bot')
    st.markdown('Ask any nutrition-related question and you\'ll get answers from both scientific research papers and social media')

    with st.form(key='my_form'):
        query = st.text_input('Enter your query:')
        submit = st.form_submit_button('Ask!')

    if submit and query is not None:

        response = requests.get('http://35.196.123.58:8060/search/'+query)
        response_json = response.json()

        respp, socmed = st.columns(2)

        with respp:
            st.subheader("Research Papers")
            # respp_ans = ''
            for ans in response_json:
                ans_index_start = ans['content'].find(ans['answer'])
                ans_index_end = ans_index_start + len(ans['answer'])
                st.markdown(ans['content'][:ans_index_start] + "`" + ans['content'][ans_index_start:ans_index_end] + "`" + ans['content'][ans_index_end:])
                # st.write(ans['content'])
                st.write(f'Score: {ans["score_y"]:.3f}')
                # respp_ans += ans['content']
                # respp_ans += f'Score: {ans["score_y"]:.3f}\n\n'
            # st.write(respp_ans)

        with socmed:
            st.subheader("Social Media")


if __name__ == '__main__':
    main()