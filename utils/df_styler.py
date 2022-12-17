def colour_df(value):
  
  if value >= 10:
    colour = 'red'
  if value <10 and value >=5:
    colour = 'orange'
  if value <5:
    colour = 'green'

  return 'color: %s' % colour

def unused_tables_colour():
  colour = 'red'
  return 'color: %s' % colour

if __name__ == "__main__":
    pass

  
