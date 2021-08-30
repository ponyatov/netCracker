package com.nc.edu.ta.ponyatov.pr2.test;

import static org.junit.Assert.*;

import com.nc.edu.ta.ponyatov.pr2.*;
import org.junit.*;

public class MyTest {

  @Test
  public void constructor() {
    Task task = new Task("constructor");
    assertEquals(task.title, "constructor");
    assertEquals(task.active, false);
  }

  @Test
  public void getter_setter() {
    Task task = new Task("getter");
    assertEquals(task.getTitle(), task.title);
    assertEquals(task.getTitle(), "getter");

    task.setTitle("setter");
    assertEquals(task.getTitle(), "setter");

    assertEquals(task.isActive(), false);
    task.setActive(true);
    assertEquals(task.isActive(), true);
    task.setActive(false);
    assertEquals(task.isActive(), false);
  }

  @Test
  public void single() {
    Task task = new Task("single");
    task.setTime(1234);
    assertEquals(task.start, 1234);
    task.setTime(5678);
    assertEquals(task.getTime(), 5678);
    assertEquals(task.getStartTime(), 5678);
    assertEquals(task.getRepeatInterval(), 0);
    assertEquals(task.isPeriodic(), false);
  }

  @Test
  public void periodic() {
    Task task = new Task("periodic");
    task.setTime(12, 34, 56);
    assertEquals(task.getStartTime(), 12);
    assertEquals(task.getEndTime(), 34);
    assertEquals(task.getRepeatInterval(), 56);
    assertEquals(task.isPeriodic(), true);
  }

  @Test
  public void dump() {
    Task taskA = new Task("A");
    assertEquals(taskA.toString(), "Task \"A\" is inactive");

    Task taskB = new Task("B", 1234, true);
    assertEquals(taskB.toString(), "Task \"B\" at 1234");

    Task taskC = new Task("C", 12, 34, 56, true);
    assertEquals(taskC.toString(), "Task \"C\" from 12 to 34 every 56 seconds");
  }

  @Test
  public void inactive_constructors() {
    Task taskA = new Task("A");
    assertEquals(taskA.toString(), "Task \"A\" is inactive");
    Task taskB = new Task("B", 1234);
    assertEquals(taskB.toString(), "Task \"B\" is inactive");
    Task taskC = new Task("C", 12, 34, 56);
    assertEquals(taskC.toString(), "Task \"C\" is inactive");
  }

  @Test
  public void change_task_type() {
    // initial (non-periodic default)
    Task task = new Task("task");
    assertEquals(task.isPeriodic(), false);
    // set time into single mode
    task.setTime(1234);
    assertEquals(task.isPeriodic(), false);
    // set time into periodic mode
    task.setTime(12, 34, 56);
    assertEquals(task.isPeriodic(), true);
  }

  @Test
  public void testNextNonRepeative() {
    Task task = new Task("some", 10, true);
    assertEquals(10, task.nextTimeAfter(0));
    assertEquals(10, task.nextTimeAfter(9));
    assertEquals(-1, task.nextTimeAfter(10));
    assertEquals(-1, task.nextTimeAfter(100));
  }

  @Test
  public void testNextRepeative() {
    Task task = new Task("some", 10, 100, 20, true);
    assertEquals(10, task.nextTimeAfter(0));
    assertEquals(10, task.nextTimeAfter(9));
    assertEquals(30, task.nextTimeAfter(10));
    assertEquals(50, task.nextTimeAfter(30));
    assertEquals(50, task.nextTimeAfter(40));
    assertEquals(-1, task.nextTimeAfter(95));
    assertEquals(-1, task.nextTimeAfter(100));
  }
}
