def colour_df(value):
  
  if value >= 5:
    colour = 'red'
  if value <5 and value >=3:
    colour = 'orange'
  if value <3:
    colour = 'green'

  return 'color: %s' % colour

if __name__ == "__main__":
    pass

  
