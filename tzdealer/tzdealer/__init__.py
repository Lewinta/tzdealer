def get_lucky_comb(array_numb, amt, comb=2):
   from itertools import combinations 

   main  = array_numb
   inve  = mixed = []
   ppc   = dif = total_c = total_n = left = 0
   for m in main:
      inve.append(m[1]+m[0])

   # Create combinations
   mixed  = list(combinations(main + inve, comb))
   # Let's remove duplicates
   mixed = remove_equals(list(set(mixed)))
   print("main: {}\ninve: {}".format(main, inve))
   for idx, m in enumerate(mixed):
      print("{}\t{}".format(idx + 1, m))
   ppc = int(amt/len(mixed))
   dif = amt - (ppc * len(mixed))
   ppn = dif / (len(array_numb) * 2)
   toc = ppc *  len(mixed)
   ton = ppn *  len(array_numb) * 2
   lef = amt - toc - ton
   print("ppc: {} tot: {}".format(ppc, toc))
   print("ppn: {} tot: {}".format(ppn, ton))
   print("lef: {} ".format(lef))

def remove_equals(array_numb):
   idx = 0
   for el in array_numb:
      inverse = (el[1], el[0])
      if inverse in array_numb:
         array_numb.pop(idx)
      idx += 1
   return array_numb