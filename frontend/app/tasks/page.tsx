"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = "http://127.0.0.1:8000";

type Subtask = {
  id: number;
  task_id: number;
  title: string;
  description?: string | null;
  status?: string;
  is_active?: boolean;
  created_by: number;
  created_at: string;
  updated_at: string;
};

type Task = {
  id: number;
  name: string;
  description?: string | null;
  project_id: number;
  team_id?: number | null;
  assigned_to?: number | null;
  status?: string;
  priority?: string;
  start_date?: string | null;
  due_date?: string | null;
  progress?: number;
  is_active?: boolean;
  created_by: number;
  created_at: string;
  updated_at: string;
  subtasks?: Subtask[];
};

type Project = {
  id: number;
  name: string;
  status?: string;
};

type TaskForm = {
  name: string;
  description: string;
  project_id: string;
  team_id: string;
  assigned_to: string;
  status: string;
  priority: string;
  start_date: string;
  due_date: string;
  progress: string;
};

const EMPTY_FORM: TaskForm = {
  name: "",
  description: "",
  project_id: "",
  team_id: "",
  assigned_to: "",
  status: "todo",
  priority: "medium",
  start_date: "",
  due_date: "",
  progress: "0",
};

export default function TasksPage() {
  const router = useRouter();

  const [tasks, setTasks] = useState<Task[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);

  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const [error, setError] = useState("");
  const [createError, setCreateError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [showCreateModal, setShowCreateModal] = useState(false);

  const [search, setSearch] = useState("");
  const [projectFilter, setProjectFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");

  const [form, setForm] = useState<TaskForm>(EMPTY_FORM);

  useEffect(() => {
    loadPage();
  }, []);

  function getToken() {
    if (typeof window === "undefined") {
      return null;
    }

    return (
      localStorage.getItem("treeflow_access_token") ||
      sessionStorage.getItem("treeflow_access_token")
    );
  }

  function clearAuth() {
    localStorage.removeItem("treeflow_access_token");
    localStorage.removeItem("treeflow_token_type");

    sessionStorage.removeItem("treeflow_access_token");
    sessionStorage.removeItem("treeflow_token_type");
  }

  async function authenticatedFetch(url: string, options?: RequestInit) {
    const token = getToken();

    if (!token) {
      clearAuth();
      router.replace("/");
      throw new Error("Authentication required.");
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
        ...(options?.headers || {}),
      },
      cache: "no-store",
    });

    if (response.status === 401) {
      clearAuth();
      router.replace("/");
      throw new Error("Your session has expired.");
    }

    return response;
  }

  async function loadPage() {
    setLoading(true);
    setError("");

    try {
      const [tasksResponse, projectsResponse] = await Promise.all([
        authenticatedFetch(`${API_BASE_URL}/api/v1/tasks/`),
        authenticatedFetch(`${API_BASE_URL}/api/v1/projects/`),
      ]);

      const tasksData = await readJson(tasksResponse);
      const projectsData = await readJson(projectsResponse);

      if (!tasksResponse.ok) {
        throw new Error(
          getApiErrorMessage(tasksData, "Unable to load tasks.")
        );
      }

      if (!projectsResponse.ok) {
        throw new Error(
          getApiErrorMessage(projectsData, "Unable to load projects.")
        );
      }

      setTasks(Array.isArray(tasksData) ? tasksData : []);
      setProjects(Array.isArray(projectsData) ? projectsData : []);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to load tasks.");
      }
    } finally {
      setLoading(false);
    }
  }

  function openCreateModal() {
    setCreateError("");
    setSuccessMessage("");

    setForm({
      ...EMPTY_FORM,
      project_id:
        projectFilter !== "all"
          ? projectFilter
          : projects.length === 1
            ? String(projects[0].id)
            : "",
    });

    setShowCreateModal(true);
  }

  function closeCreateModal() {
    if (creating) {
      return;
    }

    setShowCreateModal(false);
    setCreateError("");
  }

  function updateForm(field: keyof TaskForm, value: string) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function createTask(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setCreateError("");
    setSuccessMessage("");

    if (!form.name.trim()) {
      setCreateError("Task name is required.");
      return;
    }

    const projectId = Number(form.project_id);

    if (
      !form.project_id ||
      !Number.isInteger(projectId) ||
      projectId <= 0
    ) {
      setCreateError("Please select a valid project.");
      return;
    }

    const progress = Number(form.progress);

    if (
      Number.isNaN(progress) ||
      progress < 0 ||
      progress > 100
    ) {
      setCreateError("Progress must be between 0 and 100.");
      return;
    }

    if (
      form.start_date &&
      form.due_date &&
      form.start_date > form.due_date
    ) {
      setCreateError("Start date cannot be after due date.");
      return;
    }

    setCreating(true);

    try {
      const payload = {
        name: form.name.trim(),
        description: form.description.trim() || null,
        project_id: projectId,

        team_id: form.team_id.trim()
          ? Number(form.team_id)
          : null,

        assigned_to: form.assigned_to.trim()
          ? Number(form.assigned_to)
          : null,

        status: form.status,
        priority: form.priority,

        start_date: form.start_date
          ? `${form.start_date}T00:00:00`
          : null,

        due_date: form.due_date
          ? `${form.due_date}T23:59:59`
          : null,

        progress: Math.round(progress),
        is_active: true,
      };

      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/tasks/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      const data = await readJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(data, "Unable to create task.")
        );
      }

      setShowCreateModal(false);
      setForm(EMPTY_FORM);

      setSuccessMessage("Task created successfully.");

      await loadPage();

      window.setTimeout(() => {
        setSuccessMessage("");
      }, 4000);
    } catch (err) {
      if (err instanceof Error) {
        setCreateError(err.message);
      } else {
        setCreateError("Unable to create task.");
      }
    } finally {
      setCreating(false);
    }
  }

  const filteredTasks = useMemo(() => {
    const query = search.trim().toLowerCase();

    return tasks.filter((task) => {
      const matchesSearch =
        !query ||
        task.name.toLowerCase().includes(query) ||
        (task.description || "").toLowerCase().includes(query) ||
        String(task.id).includes(query);

      const matchesProject =
        projectFilter === "all" ||
        String(task.project_id) === projectFilter;

      const matchesStatus =
        statusFilter === "all" ||
        normalizeValue(task.status) === statusFilter;

      const matchesPriority =
        priorityFilter === "all" ||
        normalizeValue(task.priority) === priorityFilter;

      return (
        matchesSearch &&
        matchesProject &&
        matchesStatus &&
        matchesPriority
      );
    });
  }, [
    tasks,
    search,
    projectFilter,
    statusFilter,
    priorityFilter,
  ]);

  const todoCount = tasks.filter(
    (task) => normalizeValue(task.status) === "todo"
  ).length;

  const inProgressCount = tasks.filter(
    (task) => normalizeValue(task.status) === "in_progress"
  ).length;

  const completedCount = tasks.filter(
    (task) => normalizeValue(task.status) === "done"
  ).length;

  const overdueCount = tasks.filter((task) => {
    if (!task.due_date) {
      return false;
    }

    if (
      ["done", "cancelled"].includes(
        normalizeValue(task.status)
      )
    ) {
      return false;
    }

    return new Date(task.due_date).getTime() < Date.now();
  }).length;

  function getProjectName(projectId: number) {
    return (
      projects.find((project) => project.id === projectId)?.name ||
      `Project #${projectId}`
    );
  }

  function logout() {
    clearAuth();
    router.replace("/");
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-slate-800 bg-[#101828] text-white lg:flex lg:flex-col">
        <div className="flex h-20 items-center border-b border-white/10 px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold">
              T
            </div>

            <div>
              <h1 className="font-bold">TreeFlow AI</h1>
              <p className="text-xs text-slate-400">
                Smart Work Management
              </p>
            </div>
          </div>
        </div>

        <nav className="flex-1 space-y-2 p-4">
          <NavButton
            label="Dashboard"
            onClick={() => router.push("/dashboard")}
          />

          <NavButton
            label="Projects"
            onClick={() => router.push("/projects")}
          />

          <NavButton label="Tasks" active />

          <NavButton label="Calendar" />
          <NavButton label="Chat" />
          <NavButton label="Files" />
          <NavButton label="Notifications" />
          <NavButton label="AI Assistant" />
          <NavButton label="Reports" />
        </nav>

        <div className="border-t border-white/10 p-4">
          <button
            type="button"
            onClick={logout}
            className="w-full rounded-xl px-4 py-3 text-left text-sm font-semibold text-slate-300 transition hover:bg-red-500/10 hover:text-red-300"
          >
            Sign out
          </button>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-20 flex min-h-20 items-center justify-between border-b border-slate-200 bg-white px-4 py-3 sm:px-6 lg:px-8">
          <div>
            <p className="text-sm font-medium text-slate-500">
              Workspace
            </p>

            <h2 className="text-xl font-bold">Tasks</h2>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={loadPage}
              disabled={loading}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            >
              Refresh
            </button>

            <button
              type="button"
              onClick={openCreateModal}
              disabled={projects.length === 0}
              className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              + Create Task
            </button>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          <section className="rounded-3xl bg-[#101828] p-6 text-white sm:p-8">
            <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-300">
                  Task Management
                </p>

                <h1 className="mt-3 text-3xl font-bold">
                  Manage your work
                </h1>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
                  Create, track and organize tasks across your TreeFlow
                  projects.
                </p>
              </div>

              <button
                type="button"
                onClick={openCreateModal}
                disabled={projects.length === 0}
                className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-bold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
              >
                + New Task
              </button>
            </div>
          </section>

          {successMessage && (
            <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-700">
              {successMessage}
            </div>
          )}

          {error && (
            <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm font-semibold text-red-700">
              {error}
            </div>
          )}

          {projects.length === 0 && !loading && !error && (
            <div className="mt-6 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              You need at least one project before creating a task.
            </div>
          )}

          <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            <StatCard label="Total Tasks" value={tasks.length} />
            <StatCard label="To Do" value={todoCount} />
            <StatCard label="In Progress" value={inProgressCount} />
            <StatCard label="Completed" value={completedCount} />
            <StatCard label="Overdue" value={overdueCount} />
          </section>

          <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
              <input
                type="text"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search tasks..."
                className={inputClass}
              />

              <select
                value={projectFilter}
                onChange={(event) =>
                  setProjectFilter(event.target.value)
                }
                className={inputClass}
              >
                <option value="all">All Projects</option>

                {projects.map((project) => (
                  <option key={project.id} value={String(project.id)}>
                    {project.name}
                  </option>
                ))}
              </select>

              <select
                value={statusFilter}
                onChange={(event) =>
                  setStatusFilter(event.target.value)
                }
                className={inputClass}
              >
                <option value="all">All Statuses</option>
                <option value="todo">To Do</option>
                <option value="in_progress">In Progress</option>
                <option value="review">Review</option>
                <option value="done">Done</option>
                <option value="cancelled">Cancelled</option>
              </select>

              <select
                value={priorityFilter}
                onChange={(event) =>
                  setPriorityFilter(event.target.value)
                }
                className={inputClass}
              >
                <option value="all">All Priorities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
          </section>

          <section className="mt-6">
            <div className="mb-4 flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold">Task List</h2>

                <p className="mt-1 text-sm text-slate-500">
                  {filteredTasks.length}{" "}
                  {filteredTasks.length === 1 ? "task" : "tasks"} found
                </p>
              </div>
            </div>

            {loading ? (
              <div className="rounded-2xl border border-slate-200 bg-white p-10 text-center shadow-sm">
                <p className="text-sm font-semibold text-slate-500">
                  Loading tasks...
                </p>
              </div>
            ) : filteredTasks.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-10 text-center">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-xl font-bold text-blue-600">
                  T
                </div>

                <h3 className="mt-4 font-bold">
                  No tasks found
                </h3>

                <p className="mt-2 text-sm text-slate-500">
                  Create your first task or change the current filters.
                </p>
              </div>
            ) : (
              <div className="grid gap-5 xl:grid-cols-2">
                {filteredTasks.map((task) => (
                  <TaskCard
                    key={task.id}
                    task={task}
                    projectName={getProjectName(task.project_id)}
                    onClick={() => router.push(`/tasks/${task.id}`)}
                  />
                ))}
              </div>
            )}
          </section>
        </main>
      </div>

      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
          <div className="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white shadow-2xl">
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-5">
              <div>
                <h2 className="text-xl font-bold">
                  Create Task
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Add a new task to a project.
                </p>
              </div>

              <button
                type="button"
                onClick={closeCreateModal}
                disabled={creating}
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-xl text-slate-500"
              >
                ×
              </button>
            </div>

            <form onSubmit={createTask} className="p-6">
              {createError && (
                <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
                  {createError}
                </div>
              )}

              <div className="grid gap-5 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label className={labelClass}>
                    Task Name *
                  </label>

                  <input
                    type="text"
                    value={form.name}
                    onChange={(event) =>
                      updateForm("name", event.target.value)
                    }
                    placeholder="Enter task name"
                    className={inputClass}
                    required
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className={labelClass}>
                    Description
                  </label>

                  <textarea
                    value={form.description}
                    onChange={(event) =>
                      updateForm("description", event.target.value)
                    }
                    placeholder="Describe the task..."
                    rows={4}
                    className={`${inputClass} h-auto resize-none py-3`}
                  />
                </div>

                <div>
                  <label className={labelClass}>
                    Project *
                  </label>

                  <select
                    value={form.project_id}
                    onChange={(event) =>
                      updateForm("project_id", event.target.value)
                    }
                    className={inputClass}
                    required
                  >
                    <option value="">Select Project</option>

                    {projects.map((project) => (
                      <option
                        key={project.id}
                        value={String(project.id)}
                      >
                        {project.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className={labelClass}>
                    Assigned User ID
                  </label>

                  <input
                    type="number"
                    min="1"
                    value={form.assigned_to}
                    onChange={(event) =>
                      updateForm("assigned_to", event.target.value)
                    }
                    placeholder="Optional"
                    className={inputClass}
                  />
                </div>

                <div>
                  <label className={labelClass}>
                    Team ID
                  </label>

                  <input
                    type="number"
                    min="1"
                    value={form.team_id}
                    onChange={(event) =>
                      updateForm("team_id", event.target.value)
                    }
                    placeholder="Optional"
                    className={inputClass}
                  />
                </div>

                <div>
                  <label className={labelClass}>
                    Status
                  </label>

                  <select
                    value={form.status}
                    onChange={(event) =>
                      updateForm("status", event.target.value)
                    }
                    className={inputClass}
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="review">Review</option>
                    <option value="done">Done</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>

                <div>
                  <label className={labelClass}>
                    Priority
                  </label>

                  <select
                    value={form.priority}
                    onChange={(event) =>
                      updateForm("priority", event.target.value)
                    }
                    className={inputClass}
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>

                <div>
                  <label className={labelClass}>
                    Start Date
                  </label>

                  <input
                    type="date"
                    value={form.start_date}
                    onChange={(event) =>
                      updateForm("start_date", event.target.value)
                    }
                    className={inputClass}
                  />
                </div>

                <div>
                  <label className={labelClass}>
                    Due Date
                  </label>

                  <input
                    type="date"
                    value={form.due_date}
                    onChange={(event) =>
                      updateForm("due_date", event.target.value)
                    }
                    className={inputClass}
                  />
                </div>

                <div className="sm:col-span-2">
                  <div className="flex items-center justify-between">
                    <label className={labelClass}>
                      Progress
                    </label>

                    <span className="text-sm font-bold text-blue-600">
                      {form.progress}%
                    </span>
                  </div>

                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="1"
                    value={form.progress}
                    onChange={(event) =>
                      updateForm("progress", event.target.value)
                    }
                    className="mt-2 w-full accent-blue-600"
                  />
                </div>
              </div>

              <div className="mt-7 flex justify-end gap-3 border-t border-slate-100 pt-5">
                <button
                  type="button"
                  onClick={closeCreateModal}
                  disabled={creating}
                  className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700 disabled:opacity-60"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={creating}
                  className="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
                >
                  {creating ? "Creating..." : "Create Task"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

function NavButton({
  label,
  active = false,
  onClick,
}: {
  label: string;
  active?: boolean;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`w-full rounded-xl px-4 py-3 text-left text-sm font-medium transition ${
        active
          ? "bg-blue-600 text-white"
          : "text-slate-300 hover:bg-white/5 hover:text-white"
      }`}
    >
      {label}
    </button>
  );
}

function StatCard({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-3xl font-bold text-slate-900">
        {value}
      </p>
    </div>
  );
}

function TaskCard({
  task,
  projectName,
  onClick,
}: {
  task: Task;
  projectName: string;
  onClick: () => void;
}) {
  const progress = Math.min(Math.max(task.progress ?? 0, 0), 100);

  return (
    <button
      type="button"
      onClick={onClick}
      className="w-full text-left"
    >
      <article className="h-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-bold uppercase tracking-wide text-blue-600">
              Task #{task.id}
            </p>

            <h3 className="mt-2 text-lg font-bold text-slate-900">
              {task.name}
            </h3>

            <p className="mt-1 text-sm font-medium text-slate-500">
              {projectName}
            </p>
          </div>

          <PriorityBadge priority={task.priority || "medium"} />
        </div>

        <p className="mt-4 line-clamp-2 min-h-10 text-sm leading-5 text-slate-500">
          {task.description || "No description provided."}
        </p>

        <div className="mt-5 flex flex-wrap gap-2">
          <StatusBadge status={task.status || "todo"} />

          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
            {task.subtasks?.length ?? 0} subtasks
          </span>
        </div>

        <div className="mt-5">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-500">
              Progress
            </span>

            <span className="font-bold text-slate-700">
              {progress}%
            </span>
          </div>

          <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-blue-600"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        <div className="mt-5 flex items-center justify-between border-t border-slate-100 pt-4">
          <div>
            <p className="text-xs text-slate-400">Due Date</p>

            <p className="mt-1 text-sm font-semibold text-slate-700">
              {formatDate(task.due_date)}
            </p>
          </div>

          <p className="text-xs font-bold text-blue-600">
            View Task →
          </p>
        </div>
      </article>
    </button>
  );
}

function StatusBadge({ status }: { status: string }) {
  const normalized = normalizeValue(status);

  const labels: Record<string, string> = {
    todo: "To Do",
    in_progress: "In Progress",
    review: "Review",
    done: "Done",
    cancelled: "Cancelled",
  };

  let classes = "bg-slate-100 text-slate-700";

  if (normalized === "in_progress") {
    classes = "bg-blue-100 text-blue-700";
  } else if (normalized === "review") {
    classes = "bg-amber-100 text-amber-700";
  } else if (normalized === "done") {
    classes = "bg-emerald-100 text-emerald-700";
  } else if (normalized === "cancelled") {
    classes = "bg-red-100 text-red-700";
  }

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-bold ${classes}`}
    >
      {labels[normalized] || status}
    </span>
  );
}

function PriorityBadge({ priority }: { priority: string }) {
  const normalized = normalizeValue(priority);

  let classes = "bg-slate-100 text-slate-700";

  if (normalized === "low") {
    classes = "bg-emerald-100 text-emerald-700";
  } else if (normalized === "medium") {
    classes = "bg-blue-100 text-blue-700";
  } else if (normalized === "high") {
    classes = "bg-orange-100 text-orange-700";
  } else if (normalized === "critical") {
    classes = "bg-red-100 text-red-700";
  }

  return (
    <span
      className={`rounded-full px-3 py-1 text-xs font-bold capitalize ${classes}`}
    >
      {priority}
    </span>
  );
}

function normalizeValue(value?: string | null) {
  return (value || "")
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "_");
}

function formatDate(value?: string | null) {
  if (!value) {
    return "Not set";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(date);
}

async function readJson(response: Response): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function getApiErrorMessage(data: unknown, fallback: string) {
  if (
    typeof data === "object" &&
    data !== null &&
    "detail" in data
  ) {
    const detail = (data as { detail?: unknown }).detail;

    if (typeof detail === "string") {
      return detail;
    }

    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) => {
          if (
            typeof item === "object" &&
            item !== null &&
            "msg" in item
          ) {
            return String(
              (item as { msg?: unknown }).msg || ""
            );
          }

          return "";
        })
        .filter(Boolean);

      if (messages.length > 0) {
        return messages.join(", ");
      }
    }
  }

  return fallback;
}

const labelClass =
  "mb-2 block text-sm font-semibold text-slate-700";

const inputClass =
  "h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10";