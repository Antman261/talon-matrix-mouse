matrix show: user.mouse_grid_start()
matrix clear: user.mouse_grid_stop()
[vox] move <user.letters>: user.vox_mouse_grid_move(letters)
matrix (<user.letters> | <user.number_key>):
  input = letters or number_key
  user.vox_mouse(input)
matrix right (<user.letter> | <user.number_key>):
  input = letter or number_key
  user.vox_mouse(input, "right")
