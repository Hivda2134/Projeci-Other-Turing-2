import pandas as pd
import numpy as np

def generate_toxic_signals(num_samples=1000):
    """
    Generates synthetic toxic signals data for calibration and testing.
    This data is privacy-safe and redacted, focusing on patterns rather than real content.
    """
    data = {
        'text_sample': [],
        'is_toxic': [],
        'hex_like_pattern': [],
        'base64_like_pattern': [],
        'entropy_score': []
    }

    for i in range(num_samples):
        is_toxic = np.random.choice([0, 1], p=[0.8, 0.2]) # 20% toxic samples
        text = ""
        hex_like = 0
        base64_like = 0
        entropy = np.random.uniform(0.1, 0.9)

        if is_toxic:
            # Generate toxic-like patterns
            if np.random.rand() < 0.5:
                # Hex-like pattern
                text = ''.join(np.random.choice(list('0123456789abcdef'), size=np.random.randint(16, 64)))
                hex_like = 1
            else:
                # Base64-like pattern
                text = ''.join(np.random.choice(list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='), size=np.random.randint(24, 96)))
                base64_like = 1
            # Introduce some noise or make it slightly less obvious
            if np.random.rand() < 0.3: # 30% chance to add some non-pattern text
                text = "random_prefix_" + text + "_random_suffix"
            entropy = np.random.uniform(0.7, 0.95) # Higher entropy for toxic
        else:
            # Generate non-toxic patterns (more natural language like)
            words = ['hello', 'world', 'python', 'code', 'example', 'function', 'data', 'analysis', 'project', 'test']
            text = ' '.join(np.random.choice(words, size=np.random.randint(5, 15)))
            entropy = np.random.uniform(0.1, 0.6) # Lower entropy for non-toxic

        data['text_sample'].append(text)
        data['is_toxic'].append(is_toxic)
        data['hex_like_pattern'].append(hex_like)
        data['base64_like_pattern'].append(base64_like)
        data['entropy_score'].append(entropy)

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    df = generate_toxic_signals(num_samples=2000)
    output_path = "data/toxic_signals_v1.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated synthetic toxic signals data to {output_path}")


