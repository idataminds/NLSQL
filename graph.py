import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from db import run_query
from db import run_query, get_schema_info

# Load environment variables from .env
load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_sql(state):
    """Use LLM to generate SQL query from user question."""
    user_question = state["question"]

    # Fetch DB schema dynamically
    schema = get_schema_info()
    schema_text = "\n".join([f"{t}: {', '.join(c)}" for t, c in schema.items()])

    prompt = f"""
    You are a MySQL expert.
    The database has the following tables and columns:

    {schema_text}

    Based on the question below, generate a valid MySQL query.
    Return ONLY the SQL query, no markdown or explanation.

    Question: {user_question}
    """
    sql = llm.invoke(prompt).content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()

    return {**state, "sql": sql}


def execute_sql(state):
    """Run SQL query and fetch results"""
    sql = state["sql"]
    try:
        results, columns  = run_query(sql)
        return {**state, "results": results, "columns": columns}
    except Exception as e:
        # Capture error and let LLM decide if it can fix it
        error_message = str(e)

        # Optional: Try asking LLM to fix query
        fix_prompt = f"""
        The following SQL query caused an error:

        Query: {sql}
        Error: {error_message}

        Please suggest a corrected MySQL query based on the same question: {state["question"]}
        Return ONLY the corrected SQL query, no explanation, no markdown.
        """

        try:
            fixed_sql = llm.invoke(fix_prompt).content.strip()
            fixed_sql = fixed_sql.replace("```sql", "").replace("```", "").strip()
            results = run_query(fixed_sql)
            return {**state, "sql": fixed_sql, "results": results}
        except Exception as e2:
            return {**state, "results": f"Could not execute query. Error: {e2}"}

workflow = StateGraph(dict)
workflow.add_node("generate_sql", generate_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.set_entry_point("generate_sql")
workflow.add_edge("generate_sql", "execute_sql")
workflow.add_edge("execute_sql", END)

graph = workflow.compile()
