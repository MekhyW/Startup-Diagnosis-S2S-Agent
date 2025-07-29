from decrypt import decrypt_system_prompt

def test_decrypt_and_print():
    """Test function to decrypt and print the system prompt."""
    try:
        decrypted_prompt = decrypt_system_prompt()
        if decrypted_prompt:
            print("=== DECRYPTED SYSTEM PROMPT ===")
            print(decrypted_prompt)
            print("=== END OF PROMPT ===")
        else:
            print("Failed to decrypt the system prompt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_decrypt_and_print()