import seaborn as sns
import matplotlib.pyplot as plt

def rgb_to_hex(rgb):
    """Convert RGB to hexadecimal color code."""
    return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])

def generate_palette(input_colors, n_colors=10):
    # Convert RGB to hexadecimal
    input_colors_hex = [rgb_to_hex(color) for color in input_colors]

    # Create a palette using the input colors
    base_palette = sns.color_palette(input_colors_hex)

    # Generate a smooth color palette with n_colors
    smooth_palette = sns.color_palette("viridis", n_colors=n_colors)

    # Combine the base palette with the smooth palette
    combined_palette = base_palette + smooth_palette

    return combined_palette

if __name__ == "__main__":
    # Replace these RGB values with your input colors
    input_colors = [(93, 65, 116), (0, 255, 221), (89, 68, 20)]

    # Number of colors in the final palette
    n_colors = 10

    # Generate the palette
    palette = generate_palette(input_colors, n_colors)

    # Plot the color palette
    sns.palplot(palette)

    # Show the plot
    plt.show()
