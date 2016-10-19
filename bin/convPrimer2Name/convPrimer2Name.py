from pprint import pprint
import appex, ui
import sys
import re
from collections import defaultdict


def pythontree():
  """Python's idiosyncratic tree.
  """
  return defaultdict(pythontree)


def make_button_item(action, image_name):
  """Returns an 'iu.Button' instance. 
  """
  return ui.ButtonItem(
    action=action, image=ui.Image.named(image_name))
    
    
class TableViewDataSource_Root():
  def __init__(self):
    if appex.is_running_extension():
      # TODO: change 'primer_test_list.txt' to real primer list
      gene2num, num2gene, num2name = get_structured_primer_file("primer_test_list.txt")
    
      self.text = appex.get_text()
    
      # Tree structure: {gene symbol: {primer number: primer name}
      self.res = pythontree()
      # We have all the Eurofins primer numbers in 'text', so search for them.
      for num in re.finditer(r'\d+', self.text):
        num = int(num.group())
        try:
          self.res[num2gene[num]][str(num)] = num2name[num]
        except KeyError:
          pass
          #sys.exit(
            #"Primer number '{}' in text could not be found in primer "
            #"file.".format(num))
      
      pprint(self.res)

  def tableview_number_of_sections(self, tableview):
    # Return the number of sections (defaults to 1)
    return 1

  def tableview_number_of_rows(self, tableview, section):
    # Return the number of rows in the section
    return 0

  def tableview_cell_for_row(self, tableview, section, row):
    # Create and return a cell for the given section/row
    cell = ui.TableViewCell()
    cell.text_label.text = 'Foo Bar'
    return cell

  def tableview_title_for_header(self, tableview, section):
    # Return a title for the given section.
    # If this is not implemented, no section headers will be shown.
    return 'Some Section'

  def tableview_can_delete(self, tableview, section, row):
    # Return True if the user should be able to delete the given row.
    return True

  def tableview_can_move(self, tableview, section, row):
    # Return True if a reordering control should be shown for the given row (in editing mode).
    return True

  def tableview_delete(self, tableview, section, row):
    # Called when the user confirms deletion of the given row.
    pass

  def tableview_move_row(self, tableview, from_section, from_row, to_section, to_row):
    # Called when the user moves a row with the reordering control (in editing mode).
    pass


class ShowNavigationView(ui.View):
  def __init__(self):
    self.root_view = ui.load_view()
    self.root_view.left_button_items  = [
      make_button_item(self.bt_close, 'iob:close_round_24')]
    self.root_view.right_button_items = [
      make_button_item(self.bt_table_view_1, 'iob:chevron_right_24')]
    tv_0 = self.root_view['table_view_0']
    tv_0.data_source = tv_0.delegate = TableViewDataSource_Root()
      
    self.table_view_1 = ui.load_view('table_view_1.pyui')
    tv_1 = self.table_view_1['table_view_1'] # Subview

    self.nav_view = ui.NavigationView(self.root_view)
    self.nav_view.present(hide_title_bar=True)
      
  def bt_table_view_1(self, sender):
    self.nav_view.push_view(self.table_view_1)

  def bt_close(self, sender):
    self.nav_view.close()
        
  def bt_action(self, sender):
    print('action from ' + sender.name)


def split_primer_name(primer_name, normalize_format=True):
  """Splits the given 'primer_name' in a tuple:
      (gene_symbol, exon_number, DNA_strand)
    and returns it. 'primer_name' must have the following format:
      '([A-Za-z0-9]+)_*([Ee][Xx]([Oo][Nn])?\d+)_*([Ff]([Oo][Rr])?|[Rr]([Ee][Vv])?)'
    If 'normalize_format' is set to 'True' some consistency
    formatting will be applied. 
  """
  m = re.fullmatch(
    r'([A-Za-z0-9]+)_*([Ee][Xx](?:[Oo][Nn])?\d+)_*([Ff](?:[Oo][Rr])?|[Rr](?:[Ee][Vv])?)',
    primer_name)
    
  if m:
    gene_symb, exon_num, strand = m.group(1), m.group(2), m.group(3)
  else:
    sys.exit(
      "Could not parse this (wrong) primer name: "
      "{}".format(primer_name))
    
  if normalize_format:
    # Make gene symbol uppercase.
    gene_symb = gene_symb.upper()
    # Make exon number lowercase.
    exon_num = exon_num.lower()
    # Make DNA strand lowercase.
    strand = strand.lower()
  
  return gene_symb, exon_num, strand
  
  
def get_structured_primer_file(primer_file):
  """Returns two dictionaries:
    1) HGNC gene symbol -> list of all corresponding Primer number
    2) Primer number -> Primer name
  If no data structures can be returned or data structures
  would be corrupt, function exits the script.
  """
  gene2num = defaultdict(list)
  num2name = {}
  
  with open(primer_file, 'r') as fh:
    for line_no, line in enumerate(fh):
      # Ignore comment and empty lines.
      if re.match(r'^\s*#|^\s*$', line):
        continue
        
      m = re.split(r'\s+', line)  # Split line at whitespace.
      if len(m) > 1:
        # Analyze match
        try:
          primer_num, primer_name = int(m[0]), m[1]
        except ValueError: # Not a primer number at position 0.
          try:  # Maybe turned around.
            primer_num, primer_name = int(m[1]), m[0]
          except ValueError: # Again not a primer number.
            sys.exit(
              "Can not find a primer number at line '{}' at "
              "position 0 or 1: '{}''".format(line_no, line))
            
        gene_symb, exon_num, strand = split_primer_name(
          primer_name,
          normalize_format=True)
          
        # Concatenate (normalized) primer name again.
        primer_name = "_".join([gene_symb, exon_num, strand])
        
        gene2num[gene_symb].append(primer_num)
        num2gene = {n: gene for gene, num_list
          in gene2num.items() for n in num_list}
        num2name.update({primer_num: primer_name})
        
      else: # len(m) not greater 1 -> not a line with correct pattern.
        pass
        
    return gene2num, num2gene, num2name
        

def main():
  

    ShowNavigationView() # Show GUI

if __name__ == "__main__":
  main()
