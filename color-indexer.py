# generate an HTML doc that shows the colors from the color list (RGBs) and what their 'color number' (index) is
import colors

def generate_html(rgb_list):
    html_content = '''
    <html>
    <head>
        <style>
            .color-box {
                display: inline-block;
                width: 50px;
                height: 50px;
                margin-right: 10px;
                vertical-align: middle;
            }
        </style>
    </head>
    <body>
    '''

    # Iterate over RGB values and append to HTML
    for index, rgb in enumerate(rgb_list):
        color = 'rgb({},{},{})'.format(*rgb)
        html_content += '<div><span class="color-box" style="background-color:{}"></span>Index: {}</div>'.format(color, index)

    # End HTML structure
    html_content += '''
    </body>
    </html>
    '''
    
    return html_content

rgb_values = colors.color_list

if __name__ == '__main__':
    html_content = generate_html(rgb_values)
    with open('colors_with_indices.html', 'w') as file:
        file.write(html_content)
