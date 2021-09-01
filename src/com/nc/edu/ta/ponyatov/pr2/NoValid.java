package com.nc.edu.ta.ponyatov.pr2;

/** Diagnostic object for parameter validation */
class NoValid {
  /**
   * create diagnostic message and abort execution
   *
   * @param where object where error occurs
   * @param msg diagnostic message
   */
  public NoValid(Object where, String msg) {
    String clazz = where.getClass().getName();
    StackTraceElement[] elements = Thread.currentThread().getStackTrace();
    int lineno = elements[2].getLineNumber();
    String file = class2file(clazz);
    //
    System.out.println("\n\n" + file + ":" + lineno + " @ " + msg + "\n\n");
    //
    for (StackTraceElement element : elements) {
      String stackClass = element.getClassName();
      String stackFile = class2file(stackClass);
      int stackLine = element.getLineNumber();
      String stackMethod = element.getMethodName();
      if (stackClass.contains("com.nc.edu") && stackMethod != "<init>")
        System.out.printf("%55s:%d\t%s\n", stackFile, stackLine, stackMethod);
    }
    //
    System.exit(-1);
  }

  /** convert dotted package name to source code file name (for VSCode) */
  private String class2file(String clazz) {
    return "src/" + clazz.replace(".", "/") + ".java";
  }
}
