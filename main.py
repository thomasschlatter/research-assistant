from components.brainstormer import generate_research_paper_idea

def main():
    print("Scientific Brainstorming Assistant")
    print("=================================")
    
    # Get scientific field input
    field = "Linguistics" # input("Enter your scientific field of research (e.g., Biology, Physics, Chemistry): ")
    
    # Get sub-field input
    sub_field = "Sound Symbolism" # input(f"Enter your sub-field in {field} (e.g., for Linguistics: Phonetics, Syntax, Computational Linguistics): ")
    
    # Set number of refinement iterations
    iterations = 3
    
    print(f"\nGenerating and refining ideas for {field} - {sub_field}")
    print("Follow the prompts to refine the generated ideas.\n")
    
    # Call the brainstorming function with both field and sub-field
    final_idea = generate_research_paper_idea(field, sub_field, num_iterations=iterations)
    
    print("\nFinal Research Concept:")
    print("=====================")
    print(final_idea)

if __name__ == "__main__":
    main()
