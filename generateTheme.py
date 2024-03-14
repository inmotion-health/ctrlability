from qt_material import export_theme
THEME="dark_blue.xml"

export_theme(theme=THEME, 
             qss='dark_teal.qss', 
             rcc='resources.rcc',
             output='theme', 
             prefix='icon:/', 
             invert_secondary=False, 
            )

