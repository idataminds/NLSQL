from graph import graph

def main():
    question = input("Ask your question: ")

    result = graph.invoke({"question": question})

    print("\n--- SQL Query Fired ---")
    print(result["sql"])

    print("\n--- Query Results ---")
    print(result["results"])

if __name__ == "__main__":
    main()
