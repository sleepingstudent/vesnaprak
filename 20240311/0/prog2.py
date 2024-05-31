import cmd
from calendar import TextCalendar


class c1(cmd.Cmd):
    prompt = ":->"
   
    def do_prmonth(self, args):
        args = args.split()
        TextCalendar().prmonth(int(args[0]), int(args[1]))
    
    def do_pryear(self, args):
        args = args.split()
        TextCalendar().pryear(int(args[0]), int(args[1]))

if __name__ == "__main__":
    c1().cmdloop()
