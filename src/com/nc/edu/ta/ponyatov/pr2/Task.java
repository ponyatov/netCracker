package com.nc.edu.ta.ponyatov.pr2;

public class Task {
  /** TODO: access to PRIVATE fields from jUnit */

  /** task title */
  public String title;

  /** single/periodic mode selector */
  private boolean periodic;
  /** single task period, seconds */
  public int start;
  /** + periodic task parameters, seconds */
  public int end, repeat;

  /** is current task active flag */
  public boolean active;

  /**
   * create single-time task
   *
   * @param title task value, non-empty, limited with 99 chars max
   * @param time activation time, seconds
   * @param active initial task state
   */
  public Task(String title, int time, boolean active) {
    this.periodic = false;
    this.setTitle(title);
    this.setTime(time);
    this.setActive(active);
  }

  /**
   * create single-time non-active task
   *
   * @see #Task(String, int, boolean)
   */
  public Task(String title) {
    this(title, 0, false);
  }

  /**
   * create inactive single task
   *
   * @see #Task(String, int, boolean)
   */
  public Task(String title, int time) {
    this(title, time, false);
  }

  /**
   * create periodic task
   *
   * @param title task value, non-empty, limited with 99 chars max
   * @param start activation time, seconds
   * @param end of task, seconds
   * @param repeat interval, seconds
   * @param active initial task state
   */
  public Task(String title, int start, int end, int repeat, boolean active) {
    this(title);
    this.setTime(start, end, repeat);
    this.setActive(active);
  }

  /**
   * create inactive periodic task
   *
   * @see #Task(String, int, int, int, boolean)
   */
  public Task(String title, int start, int end, int repeat) {
    this(title, start, end, repeat, false);
  }

  /** @return {@link #title} */
  public String getTitle() {
    return title;
  }

  /** * @param title task value, non-empty, limited with 99 chars max */
  public void setTitle(String title) {
    if (!(title.length() > 0)) new NoValid(this, "setTitle(title>0)");
    if (!(title.length() < 99)) new NoValid(this, "setTitle(title<99)");
    this.title = title;
  }

  /** @return is given task active */
  public boolean isActive() {
    return active;
  }

  /**
   * (de)activate task
   *
   * @param active true activate; false deactivate
   */
  public void setActive(boolean active) {
    this.active = active;
  }

  /**
   * @return {@link #start}
   *     <ul>
   *       <li>notification time for single task
   *       <li>start time for periodic task
   *     </ul>
   */
  public int getTime() {
    return start;
  }

  /**
   * change time for single task (convert periodic task to a single)
   *
   * @param time notification time, seconds
   */
  public void setTime(int time) {
    if (!(time >= 0)) new NoValid(this, "setTime(time>=0)");
    this.periodic = false;
    this.start = time;
    this.end = this.start;
    this.repeat = 0;
    if (time == 0) this.active = false;
  }

  /**
   * configure periodic task (convert single task to a periodic)
   *
   * @param start of active period, seconds
   * @param end of active period, seconds
   * @param repeat task repeat interval, seconds
   */
  public void setTime(int start, int end, int repeat) {
    if (!(start >= 0)) new NoValid(this, "setTime(start >= 0)");
    if (!(end >= start)) new NoValid(this, "setTime(end >= start)");
    if (!(repeat > 0)) new NoValid(this, "setTime(repeat > 0)");
    this.periodic = true;
    this.start = start;
    this.end = end;
    this.repeat = repeat;
    if (start == 0) this.active = false;
  }

  /** @return {@link #start} */
  public int getStartTime() {
    return start;
  }

  /** @return {@link #end} */
  public int getEndTime() {
    return end;
  }

  /**
   * @return {@link #repeat}
   *     <ul>
   *       <li>task repeat interval for periodic task
   *       <li>0 for single task
   *     </ul>
   */
  public int getRepeatInterval() {
    return repeat;
  }

  /**
   * @return {@link #periodic}
   *     <ul>
   *       <li>true for periodic tasks
   *       <li>false for single-time tasks
   *     </ul>
   */
  public boolean isPeriodic() {
    return periodic;
  }

  /** @alias {@link #isPeriodic()} */
  public boolean isRepeated() {
    return isPeriodic();
  }

  /** notification formatting */
  public String toString() {
    if (!active) {
      return String.format("Task \"%s\" is inactive", title);
    } else {
      if (periodic) {
        return String.format(
            "Task \"%s\" from %d to %d every %d seconds", title, start, end, repeat);
      } else {
        return String.format("Task \"%s\" at %d", title, start);
      }
    }
  }

  /**
   * get time of next notification starting from `time`
   *
   * @param time
   * @return
   *     <ul>
   *       <li>time of next notification, seconds
   *       <li>-1, if inactive task or there is no next notifications
   *     </ul>
   */
  public int nextTimeAfter(int time) {
    // not-active
    if (!active) return -1;
    // single task
    if (!periodic) {
      if (start > time) {
        return start;
      } else {
        return -1;
      }
    }
    // periodic task
    for (int t = start; t <= end; t += repeat) {
      if (t > time) return t;
    }
    return -1;
  }
}
