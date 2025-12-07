#!/usr/bin/env python3.12
"""
אפליקציית אימון כושר - Fitness Training App
A comprehensive fitness training application with workout tracking,
exercise library, timer, and progress statistics.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time

# Try to import ttkbootstrap for modern styling
try:
    import ttkbootstrap as ttkb
    from ttkbootstrap.constants import *
    USE_BOOTSTRAP = True
except ImportError:
    USE_BOOTSTRAP = False

# Try to import matplotlib for charts
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    USE_MATPLOTLIB = True
except ImportError:
    USE_MATPLOTLIB = False


class DataManager:
    """Manages all data persistence for the fitness app."""

    DATA_FILE = "fitness_data.json"

    # Default exercise library
    DEFAULT_EXERCISES = {
        "שכיבות סמיכה": {"category": "חזה", "calories_per_rep": 0.5, "icon": "💪"},
        "סקוואט": {"category": "רגליים", "calories_per_rep": 0.6, "icon": "🦵"},
        "מתח": {"category": "גב", "calories_per_rep": 1.0, "icon": "🏋️"},
        "כפיפות בטן": {"category": "בטן", "calories_per_rep": 0.3, "icon": "🔥"},
        "לאנג'ים": {"category": "רגליים", "calories_per_rep": 0.5, "icon": "🦵"},
        "פלאנק": {"category": "בטן", "calories_per_rep": 0.1, "icon": "🧘"},
        "בורפי": {"category": "קרדיו", "calories_per_rep": 1.5, "icon": "⚡"},
        "ג'אמפינג ג'ק": {"category": "קרדיו", "calories_per_rep": 0.2, "icon": "🏃"},
        "דיפס": {"category": "זרועות", "calories_per_rep": 0.7, "icon": "💪"},
        "כתפיים צד": {"category": "כתפיים", "calories_per_rep": 0.4, "icon": "🎯"},
    }

    DEFAULT_WORKOUTS = {
        "אימון בוקר מהיר": {
            "exercises": [
                {"name": "ג'אמפינג ג'ק", "sets": 3, "reps": 20, "rest": 30},
                {"name": "שכיבות סמיכה", "sets": 3, "reps": 10, "rest": 60},
                {"name": "סקוואט", "sets": 3, "reps": 15, "rest": 45},
                {"name": "כפיפות בטן", "sets": 3, "reps": 20, "rest": 30},
            ],
            "description": "אימון קצר ואינטנסיבי לבוקר"
        },
        "אימון חזה וזרועות": {
            "exercises": [
                {"name": "שכיבות סמיכה", "sets": 4, "reps": 12, "rest": 60},
                {"name": "דיפס", "sets": 3, "reps": 10, "rest": 60},
                {"name": "שכיבות סמיכה", "sets": 3, "reps": 8, "rest": 90},
            ],
            "description": "אימון ממוקד לפלג גוף עליון"
        },
        "אימון רגליים": {
            "exercises": [
                {"name": "סקוואט", "sets": 4, "reps": 15, "rest": 60},
                {"name": "לאנג'ים", "sets": 3, "reps": 12, "rest": 45},
                {"name": "סקוואט", "sets": 3, "reps": 20, "rest": 60},
            ],
            "description": "אימון מקיף לרגליים"
        },
        "אימון קרדיו HIIT": {
            "exercises": [
                {"name": "בורפי", "sets": 4, "reps": 10, "rest": 30},
                {"name": "ג'אמפינג ג'ק", "sets": 4, "reps": 30, "rest": 20},
                {"name": "סקוואט", "sets": 4, "reps": 20, "rest": 30},
                {"name": "בורפי", "sets": 3, "reps": 8, "rest": 45},
            ],
            "description": "אימון אינטרוולים אינטנסיבי"
        },
    }

    def __init__(self):
        self.data = self.load_data()

    def load_data(self) -> dict:
        """Load data from JSON file or create default data."""
        if os.path.exists(self.DATA_FILE):
            try:
                with open(self.DATA_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        # Return default data structure
        return {
            "exercises": self.DEFAULT_EXERCISES.copy(),
            "workouts": self.DEFAULT_WORKOUTS.copy(),
            "history": [],
            "goals": {
                "weekly_workouts": 3,
                "daily_calories": 300
            },
            "user_stats": {
                "total_workouts": 0,
                "total_calories": 0,
                "total_time_minutes": 0,
                "streak": 0,
                "best_streak": 0,
                "last_workout_date": None
            }
        }

    def save_data(self):
        """Save data to JSON file."""
        with open(self.DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_workout_to_history(self, workout_name: str, exercises_completed: List[dict],
                                duration_minutes: int, calories_burned: float):
        """Add a completed workout to history."""
        today = datetime.now().strftime("%Y-%m-%d")

        entry = {
            "date": today,
            "timestamp": datetime.now().isoformat(),
            "workout_name": workout_name,
            "exercises": exercises_completed,
            "duration_minutes": duration_minutes,
            "calories_burned": round(calories_burned, 1)
        }

        self.data["history"].append(entry)

        # Update stats
        stats = self.data["user_stats"]
        stats["total_workouts"] += 1
        stats["total_calories"] += calories_burned
        stats["total_time_minutes"] += duration_minutes

        # Update streak
        if stats["last_workout_date"]:
            last_date = datetime.strptime(stats["last_workout_date"], "%Y-%m-%d")
            today_date = datetime.strptime(today, "%Y-%m-%d")
            diff = (today_date - last_date).days

            if diff == 1:
                stats["streak"] += 1
            elif diff > 1:
                stats["streak"] = 1
        else:
            stats["streak"] = 1

        stats["best_streak"] = max(stats["streak"], stats["best_streak"])
        stats["last_workout_date"] = today

        self.save_data()

    def get_weekly_stats(self) -> dict:
        """Get statistics for the current week."""
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

        weekly_workouts = 0
        weekly_calories = 0
        weekly_minutes = 0
        daily_breakdown = {i: 0 for i in range(7)}  # 0=Monday, 6=Sunday

        for entry in self.data["history"]:
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
            if entry_date >= week_start:
                weekly_workouts += 1
                weekly_calories += entry["calories_burned"]
                weekly_minutes += entry["duration_minutes"]
                day_idx = entry_date.weekday()
                daily_breakdown[day_idx] += 1

        return {
            "workouts": weekly_workouts,
            "calories": round(weekly_calories, 1),
            "minutes": weekly_minutes,
            "daily_breakdown": daily_breakdown,
            "goal_progress": weekly_workouts / max(self.data["goals"]["weekly_workouts"], 1) * 100
        }


class ExerciseTimer:
    """Timer for exercise sets with rest periods."""

    def __init__(self, callback):
        self.callback = callback
        self.running = False
        self.paused = False
        self.seconds_remaining = 0
        self.timer_thread = None

    def start(self, seconds: int):
        """Start the timer."""
        self.seconds_remaining = seconds
        self.running = True
        self.paused = False
        self.timer_thread = threading.Thread(target=self._run, daemon=True)
        self.timer_thread.start()

    def _run(self):
        """Timer loop."""
        while self.running and self.seconds_remaining > 0:
            if not self.paused:
                time.sleep(1)
                if not self.paused and self.running:
                    self.seconds_remaining -= 1
                    self.callback(self.seconds_remaining, self.running)
            else:
                time.sleep(0.1)

        if self.running:
            self.running = False
            self.callback(0, False)

    def pause(self):
        """Pause the timer."""
        self.paused = True

    def resume(self):
        """Resume the timer."""
        self.paused = False

    def stop(self):
        """Stop the timer."""
        self.running = False
        self.paused = False


class FitnessApp:
    """Main fitness training application."""

    def __init__(self):
        self.data_manager = DataManager()
        self.timer = ExerciseTimer(self._timer_callback)
        self.current_workout = None
        self.current_exercise_index = 0
        self.current_set = 0
        self.workout_start_time = None
        self.calories_burned = 0

        self._setup_window()
        self._create_ui()
        self._update_dashboard()

    def _setup_window(self):
        """Setup the main window."""
        if USE_BOOTSTRAP:
            self.root = ttkb.Window(themename="superhero")
        else:
            self.root = tk.Tk()

        self.root.title("🏋️ אפליקציית אימון כושר")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Configure RTL support
        self.root.tk.eval('package require Tk')

    def _create_ui(self):
        """Create the main user interface."""
        # Create notebook for tabs
        if USE_BOOTSTRAP:
            self.notebook = ttkb.Notebook(self.root, bootstyle="primary")
        else:
            self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self._create_dashboard_tab()
        self._create_workout_tab()
        self._create_exercises_tab()
        self._create_history_tab()
        self._create_stats_tab()

    def _create_dashboard_tab(self):
        """Create the main dashboard tab."""
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="🏠 דף הבית")

        # Welcome section
        welcome_frame = ttk.LabelFrame(self.dashboard_frame, text="ברוכים הבאים!")
        welcome_frame.pack(fill=tk.X, padx=20, pady=10)

        self.welcome_label = ttk.Label(
            welcome_frame,
            text="בוא נתחיל לאמן! 💪",
            font=('Arial', 16, 'bold')
        )
        self.welcome_label.pack(pady=10)

        # Stats overview
        stats_frame = ttk.LabelFrame(self.dashboard_frame, text="📊 סטטיסטיקות")
        stats_frame.pack(fill=tk.X, padx=20, pady=10)

        self.stats_container = ttk.Frame(stats_frame)
        self.stats_container.pack(fill=tk.X, pady=10)

        # Create stat cards
        self.stat_labels = {}
        stats_info = [
            ("total_workouts", "🏃 אימונים", "0"),
            ("streak", "🔥 רצף", "0 ימים"),
            ("calories", "⚡ קלוריות השבוע", "0"),
            ("weekly_progress", "🎯 התקדמות שבועית", "0%"),
        ]

        for i, (key, title, default) in enumerate(stats_info):
            card = ttk.Frame(self.stats_container)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=10)

            ttk.Label(card, text=title, font=('Arial', 10)).pack()
            self.stat_labels[key] = ttk.Label(card, text=default, font=('Arial', 18, 'bold'))
            self.stat_labels[key].pack()

        # Quick start buttons
        quick_frame = ttk.LabelFrame(self.dashboard_frame, text="🚀 התחלה מהירה")
        quick_frame.pack(fill=tk.X, padx=20, pady=10)

        btn_frame = ttk.Frame(quick_frame)
        btn_frame.pack(pady=10)

        workouts = list(self.data_manager.data["workouts"].keys())[:4]
        for workout in workouts:
            if USE_BOOTSTRAP:
                btn = ttkb.Button(
                    btn_frame,
                    text=workout,
                    bootstyle="success-outline",
                    command=lambda w=workout: self._start_quick_workout(w)
                )
            else:
                btn = ttk.Button(
                    btn_frame,
                    text=workout,
                    command=lambda w=workout: self._start_quick_workout(w)
                )
            btn.pack(side=tk.LEFT, padx=5)

        # Goals section
        goals_frame = ttk.LabelFrame(self.dashboard_frame, text="🎯 יעדים שבועיים")
        goals_frame.pack(fill=tk.X, padx=20, pady=10)

        goals = self.data_manager.data["goals"]
        weekly_stats = self.data_manager.get_weekly_stats()

        # Workout goal progress
        ttk.Label(goals_frame, text=f"אימונים: {weekly_stats['workouts']}/{goals['weekly_workouts']}").pack(pady=5)
        if USE_BOOTSTRAP:
            self.workout_progress = ttkb.Progressbar(
                goals_frame,
                bootstyle="success-striped",
                maximum=goals['weekly_workouts'],
                value=weekly_stats['workouts']
            )
        else:
            self.workout_progress = ttk.Progressbar(
                goals_frame,
                maximum=max(goals['weekly_workouts'], 1),
                value=weekly_stats['workouts']
            )
        self.workout_progress.pack(fill=tk.X, padx=20, pady=5)

    def _create_workout_tab(self):
        """Create the workout execution tab."""
        self.workout_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.workout_frame, text="🏋️ אימון")

        # Workout selection
        select_frame = ttk.LabelFrame(self.workout_frame, text="בחר אימון")
        select_frame.pack(fill=tk.X, padx=20, pady=10)

        self.workout_var = tk.StringVar()
        workout_names = list(self.data_manager.data["workouts"].keys())

        if USE_BOOTSTRAP:
            self.workout_combo = ttkb.Combobox(
                select_frame,
                textvariable=self.workout_var,
                values=workout_names,
                state="readonly",
                bootstyle="primary"
            )
        else:
            self.workout_combo = ttk.Combobox(
                select_frame,
                textvariable=self.workout_var,
                values=workout_names,
                state="readonly"
            )
        self.workout_combo.pack(pady=10, padx=20, fill=tk.X)
        self.workout_combo.bind('<<ComboboxSelected>>', self._on_workout_selected)

        # Workout details
        self.details_frame = ttk.LabelFrame(self.workout_frame, text="פרטי האימון")
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.details_text = tk.Text(self.details_frame, height=10, state='disabled', font=('Arial', 11))
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Timer display
        timer_frame = ttk.LabelFrame(self.workout_frame, text="⏱️ טיימר")
        timer_frame.pack(fill=tk.X, padx=20, pady=10)

        self.timer_label = ttk.Label(timer_frame, text="00:00", font=('Arial', 48, 'bold'))
        self.timer_label.pack(pady=10)

        self.exercise_status_label = ttk.Label(timer_frame, text="בחר אימון להתחלה", font=('Arial', 14))
        self.exercise_status_label.pack(pady=5)

        # Control buttons
        btn_frame = ttk.Frame(timer_frame)
        btn_frame.pack(pady=10)

        if USE_BOOTSTRAP:
            self.start_btn = ttkb.Button(btn_frame, text="▶️ התחל", bootstyle="success",
                                         command=self._start_workout)
            self.pause_btn = ttkb.Button(btn_frame, text="⏸️ השהה", bootstyle="warning",
                                         command=self._pause_workout, state='disabled')
            self.skip_btn = ttkb.Button(btn_frame, text="⏭️ דלג", bootstyle="info",
                                        command=self._skip_rest, state='disabled')
            self.stop_btn = ttkb.Button(btn_frame, text="⏹️ סיים", bootstyle="danger",
                                        command=self._stop_workout, state='disabled')
        else:
            self.start_btn = ttk.Button(btn_frame, text="▶️ התחל", command=self._start_workout)
            self.pause_btn = ttk.Button(btn_frame, text="⏸️ השהה", command=self._pause_workout, state='disabled')
            self.skip_btn = ttk.Button(btn_frame, text="⏭️ דלג", command=self._skip_rest, state='disabled')
            self.stop_btn = ttk.Button(btn_frame, text="⏹️ סיים", command=self._stop_workout, state='disabled')

        self.start_btn.pack(side=tk.LEFT, padx=5)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        self.skip_btn.pack(side=tk.LEFT, padx=5)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

    def _create_exercises_tab(self):
        """Create the exercise library tab."""
        self.exercises_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.exercises_frame, text="📚 ספריית תרגילים")

        # Exercise list
        list_frame = ttk.LabelFrame(self.exercises_frame, text="תרגילים זמינים")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview for exercises
        columns = ('name', 'category', 'calories', 'icon')
        self.exercise_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        self.exercise_tree.heading('icon', text='')
        self.exercise_tree.heading('name', text='שם התרגיל')
        self.exercise_tree.heading('category', text='קטגוריה')
        self.exercise_tree.heading('calories', text='קלוריות/חזרה')

        self.exercise_tree.column('icon', width=50)
        self.exercise_tree.column('name', width=200)
        self.exercise_tree.column('category', width=150)
        self.exercise_tree.column('calories', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.exercise_tree.yview)
        self.exercise_tree.configure(yscrollcommand=scrollbar.set)

        self.exercise_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._populate_exercise_tree()

        # Add exercise form
        add_frame = ttk.LabelFrame(self.exercises_frame, text="➕ הוסף תרגיל חדש")
        add_frame.pack(fill=tk.X, padx=20, pady=10)

        form_frame = ttk.Frame(add_frame)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="שם:").grid(row=0, column=0, padx=5)
        self.new_exercise_name = ttk.Entry(form_frame, width=20)
        self.new_exercise_name.grid(row=0, column=1, padx=5)

        ttk.Label(form_frame, text="קטגוריה:").grid(row=0, column=2, padx=5)
        self.new_exercise_category = ttk.Entry(form_frame, width=15)
        self.new_exercise_category.grid(row=0, column=3, padx=5)

        ttk.Label(form_frame, text="קלוריות:").grid(row=0, column=4, padx=5)
        self.new_exercise_calories = ttk.Entry(form_frame, width=8)
        self.new_exercise_calories.grid(row=0, column=5, padx=5)

        if USE_BOOTSTRAP:
            add_btn = ttkb.Button(form_frame, text="הוסף", bootstyle="success", command=self._add_exercise)
        else:
            add_btn = ttk.Button(form_frame, text="הוסף", command=self._add_exercise)
        add_btn.grid(row=0, column=6, padx=10)

    def _create_history_tab(self):
        """Create the workout history tab."""
        self.history_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.history_frame, text="📅 היסטוריה")

        # History list
        list_frame = ttk.LabelFrame(self.history_frame, text="אימונים אחרונים")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ('date', 'workout', 'duration', 'calories')
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)

        self.history_tree.heading('date', text='תאריך')
        self.history_tree.heading('workout', text='סוג אימון')
        self.history_tree.heading('duration', text='משך (דקות)')
        self.history_tree.heading('calories', text='קלוריות')

        self.history_tree.column('date', width=150)
        self.history_tree.column('workout', width=200)
        self.history_tree.column('duration', width=100)
        self.history_tree.column('calories', width=100)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)

        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._populate_history_tree()

    def _create_stats_tab(self):
        """Create the statistics tab."""
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="📈 סטטיסטיקות")

        # Overall stats
        overall_frame = ttk.LabelFrame(self.stats_frame, text="סטטיסטיקות כלליות")
        overall_frame.pack(fill=tk.X, padx=20, pady=10)

        stats = self.data_manager.data["user_stats"]

        stats_text = f"""
        🏃 סה"כ אימונים: {stats['total_workouts']}
        🔥 רצף נוכחי: {stats['streak']} ימים
        ⭐ רצף שיא: {stats['best_streak']} ימים
        ⚡ סה"כ קלוריות: {round(stats['total_calories'], 1)}
        ⏱️ סה"כ זמן אימון: {stats['total_time_minutes']} דקות
        """

        self.overall_stats_label = ttk.Label(overall_frame, text=stats_text, font=('Arial', 12), justify='right')
        self.overall_stats_label.pack(pady=10, padx=20)

        # Weekly chart (if matplotlib available)
        if USE_MATPLOTLIB:
            chart_frame = ttk.LabelFrame(self.stats_frame, text="📊 אימונים השבוע")
            chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

            self._create_weekly_chart(chart_frame)

    def _create_weekly_chart(self, parent):
        """Create a weekly workout chart."""
        weekly_stats = self.data_manager.get_weekly_stats()

        fig = Figure(figsize=(6, 3), dpi=100)
        ax = fig.add_subplot(111)

        days = ['ב', 'ג', 'ד', 'ה', 'ו', 'ש', 'א']
        values = [weekly_stats['daily_breakdown'][i] for i in range(7)]

        bars = ax.bar(days, values, color='#4CAF50')
        ax.set_ylabel('אימונים')
        ax.set_title('אימונים לפי יום')
        ax.set_ylim(0, max(max(values) + 1, 3))

        for bar, val in zip(bars, values):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                       str(val), ha='center', va='bottom')

        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _populate_exercise_tree(self):
        """Populate the exercise treeview."""
        for item in self.exercise_tree.get_children():
            self.exercise_tree.delete(item)

        for name, data in self.data_manager.data["exercises"].items():
            self.exercise_tree.insert('', tk.END, values=(
                name,
                data['category'],
                data['calories_per_rep'],
                data.get('icon', '💪')
            ))

    def _populate_history_tree(self):
        """Populate the history treeview."""
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)

        # Show most recent first
        for entry in reversed(self.data_manager.data["history"][-50:]):
            self.history_tree.insert('', tk.END, values=(
                entry['date'],
                entry['workout_name'],
                entry['duration_minutes'],
                entry['calories_burned']
            ))

    def _update_dashboard(self):
        """Update dashboard statistics."""
        stats = self.data_manager.data["user_stats"]
        weekly = self.data_manager.get_weekly_stats()
        goals = self.data_manager.data["goals"]

        self.stat_labels["total_workouts"].config(text=str(stats['total_workouts']))
        self.stat_labels["streak"].config(text=f"{stats['streak']} ימים")
        self.stat_labels["calories"].config(text=str(round(weekly['calories'], 1)))
        self.stat_labels["weekly_progress"].config(text=f"{round(weekly['goal_progress'])}%")

        self.workout_progress.config(value=weekly['workouts'], maximum=max(goals['weekly_workouts'], 1))

    def _on_workout_selected(self, event=None):
        """Handle workout selection."""
        workout_name = self.workout_var.get()
        if not workout_name:
            return

        workout = self.data_manager.data["workouts"].get(workout_name)
        if not workout:
            return

        # Display workout details
        self.details_text.config(state='normal')
        self.details_text.delete(1.0, tk.END)

        text = f"📝 {workout.get('description', '')}\n\n"
        text += "תרגילים:\n"
        text += "-" * 40 + "\n"

        for i, ex in enumerate(workout['exercises'], 1):
            exercise_data = self.data_manager.data["exercises"].get(ex['name'], {})
            icon = exercise_data.get('icon', '💪')
            text += f"{i}. {icon} {ex['name']}\n"
            text += f"   {ex['sets']} סטים × {ex['reps']} חזרות | מנוחה: {ex['rest']} שניות\n\n"

        self.details_text.insert(tk.END, text)
        self.details_text.config(state='disabled')

    def _start_quick_workout(self, workout_name: str):
        """Start a workout from quick start."""
        self.notebook.select(self.workout_frame)
        self.workout_var.set(workout_name)
        self._on_workout_selected()

    def _start_workout(self):
        """Start the selected workout."""
        workout_name = self.workout_var.get()
        if not workout_name:
            messagebox.showwarning("שגיאה", "יש לבחור אימון קודם!")
            return

        self.current_workout = self.data_manager.data["workouts"][workout_name]
        self.current_exercise_index = 0
        self.current_set = 1
        self.workout_start_time = datetime.now()
        self.calories_burned = 0

        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.skip_btn.config(state='normal')
        self.stop_btn.config(state='normal')

        self._next_exercise()

    def _next_exercise(self):
        """Move to the next exercise or set."""
        if not self.current_workout:
            return

        exercises = self.current_workout['exercises']

        if self.current_exercise_index >= len(exercises):
            self._complete_workout()
            return

        current = exercises[self.current_exercise_index]
        exercise_data = self.data_manager.data["exercises"].get(current['name'], {})
        icon = exercise_data.get('icon', '💪')

        if self.current_set > current['sets']:
            # Move to next exercise
            self.current_exercise_index += 1
            self.current_set = 1
            self._next_exercise()
            return

        # Show current exercise
        status = f"{icon} {current['name']} - סט {self.current_set}/{current['sets']} ({current['reps']} חזרות)"
        self.exercise_status_label.config(text=status)

        # Calculate calories for this set
        calories = exercise_data.get('calories_per_rep', 0.5) * current['reps']
        self.calories_burned += calories

        # Ask to start rest timer after set
        self.timer_label.config(text="בצע!")
        self.root.after(2000, lambda: self._start_rest(current['rest']))

    def _start_rest(self, seconds: int):
        """Start rest timer."""
        if not self.current_workout:
            return

        self.exercise_status_label.config(text="⏸️ מנוחה...")
        self.current_set += 1
        self.timer.start(seconds)

    def _timer_callback(self, seconds: int, running: bool):
        """Timer callback - updates UI."""
        def update():
            mins, secs = divmod(seconds, 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

            if not running:
                self._next_exercise()

        self.root.after(0, update)

    def _pause_workout(self):
        """Pause or resume the workout."""
        if self.timer.paused:
            self.timer.resume()
            self.pause_btn.config(text="⏸️ השהה")
        else:
            self.timer.pause()
            self.pause_btn.config(text="▶️ המשך")

    def _skip_rest(self):
        """Skip the rest period."""
        self.timer.stop()
        self._next_exercise()

    def _stop_workout(self):
        """Stop the workout early."""
        if messagebox.askyesno("סיום אימון", "האם אתה בטוח שברצונך לסיים את האימון?"):
            self.timer.stop()
            self._complete_workout()

    def _complete_workout(self):
        """Complete the workout and save stats."""
        if self.workout_start_time:
            duration = (datetime.now() - self.workout_start_time).seconds // 60

            self.data_manager.add_workout_to_history(
                workout_name=self.workout_var.get(),
                exercises_completed=self.current_workout['exercises'] if self.current_workout else [],
                duration_minutes=max(duration, 1),
                calories_burned=self.calories_burned
            )

        messagebox.showinfo(
            "כל הכבוד! 🎉",
            f"סיימת את האימון!\n\nקלוריות שנשרפו: {round(self.calories_burned, 1)}\n"
            f"זמן אימון: {duration if self.workout_start_time else 0} דקות"
        )

        # Reset UI
        self.current_workout = None
        self.workout_start_time = None
        self.timer_label.config(text="00:00")
        self.exercise_status_label.config(text="בחר אימון להתחלה")

        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled')
        self.skip_btn.config(state='disabled')
        self.stop_btn.config(state='disabled')

        # Update dashboard
        self._update_dashboard()
        self._populate_history_tree()

    def _add_exercise(self):
        """Add a new exercise to the library."""
        name = self.new_exercise_name.get().strip()
        category = self.new_exercise_category.get().strip()

        try:
            calories = float(self.new_exercise_calories.get())
        except ValueError:
            messagebox.showerror("שגיאה", "ערך קלוריות לא תקין")
            return

        if not name or not category:
            messagebox.showerror("שגיאה", "יש למלא את כל השדות")
            return

        self.data_manager.data["exercises"][name] = {
            "category": category,
            "calories_per_rep": calories,
            "icon": "💪"
        }
        self.data_manager.save_data()

        # Clear form
        self.new_exercise_name.delete(0, tk.END)
        self.new_exercise_category.delete(0, tk.END)
        self.new_exercise_calories.delete(0, tk.END)

        # Refresh list
        self._populate_exercise_tree()
        messagebox.showinfo("הצלחה", f"התרגיל '{name}' נוסף בהצלחה!")

    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = FitnessApp()
    app.run()


if __name__ == "__main__":
    main()
