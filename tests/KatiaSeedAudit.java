import org.codeanalysis.ExecutableParser;
class KatiaSeedAudit {
 public static void main(String[] a) {
  var p = new ExecutableParser(a[0], a[1]);
  p.parse();
  System.out.println("Resolved: "+(p.getSeedMethod()!=null));
  System.out.println("Relations: "+p.getResults());
 }
}
