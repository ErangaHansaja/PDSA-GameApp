def open_knights_tour(root):
    root.destroy()
    from knightstour.app import KnightsTourApp
    app = KnightsTourApp()
    app.mainloop()
