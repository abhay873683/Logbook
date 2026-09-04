"use client";



import { FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

const API_BASE_URL = "http://127.0.0.1:8000";

type Subtask = {
  id: number;
  task_id: number;
  title: string;
  description?: string | null;
  status: string;
  is_active: boolean;
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
  created_by: number;
  status: string;
  priority: string;
  start_date?: string | null;
  due_date?: string | null;
  progress: number;
  is_active?: boolean;
  created_at: string;
  updated_at: string;
  subtasks?: Subtask[];
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
};

type TaskProgress = {
  id: number;
  task_id: number;
  user_id: number;
  progress: number;
  status: string;
  note?: string | null;
  updated_at: string;
};

type ProgressForm = {
  progress: string;
  status: string;
  note: string;
};

const EMPTY_PROGRESS_FORM: ProgressForm = {
  progress: "0",
  status: "In Progress",
  note: "",
};

type SubtaskForm = {
  title: string;
  description: string;
  status: string;
  is_active: boolean;
};

const EMPTY_SUBTASK_FORM: SubtaskForm = {
  title: "",
  description: "",
  status: "todo",
  is_active: true,
};

export default function TaskDetailsPage() {
  const router = useRouter();
  const params = useParams<{ id: string }>();
  const taskId = params.id;

  const [task, setTask] = useState<Task | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const [editError, setEditError] = useState("");
  const [deleteError, setDeleteError] = useState("");

  const [successMessage, setSuccessMessage] = useState("");

  const [showCreateSubtaskModal, setShowCreateSubtaskModal] =
    useState(false);

  const [showEditSubtaskModal, setShowEditSubtaskModal] =
    useState(false);

  const [showDeleteSubtaskModal, setShowDeleteSubtaskModal] =
    useState(false);

  const [selectedSubtask, setSelectedSubtask] =
    useState<Subtask | null>(null);

  const [subtaskForm, setSubtaskForm] =
    useState<SubtaskForm>(EMPTY_SUBTASK_FORM);

  const [subtaskSaving, setSubtaskSaving] = useState(false);
  const [subtaskDeleting, setSubtaskDeleting] =
    useState(false);

  const [subtaskError, setSubtaskError] = useState("");

  const [progressHistory, setProgressHistory] = useState<TaskProgress[]>([]);
  const [progressLoading, setProgressLoading] = useState(false);
  const [progressError, setProgressError] = useState("");
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [showDeleteProgressModal, setShowDeleteProgressModal] = useState(false);
  const [selectedProgress, setSelectedProgress] = useState<TaskProgress | null>(null);
  const [progressForm, setProgressForm] = useState<ProgressForm>(EMPTY_PROGRESS_FORM);
  const [progressSaving, setProgressSaving] = useState(false);
  const [progressDeleting, setProgressDeleting] = useState(false);

  const [form, setForm] = useState<TaskForm>({
    name: "",
    description: "",
    project_id: "",
    team_id: "",
    assigned_to: "",
    status: "todo",
    priority: "medium",
    start_date: "",
    due_date: "",
  });

  useEffect(() => {
    if (taskId) {
      loadTask();
      loadProgressHistory();
    }
  }, [taskId]);

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

  async function authenticatedFetch(
    url: string,
    options: RequestInit = {}
  ) {
    const token = getToken();

    if (!token) {
      clearAuth();
      router.replace("/");
      throw new Error("Authentication required.");
    }

    const headers = new Headers(options.headers);

    headers.set("Authorization", `Bearer ${token}`);
    headers.set("Accept", "application/json");

    const response = await fetch(url, {
      ...options,
      headers,
      cache: "no-store",
    });

    if (response.status === 401) {
      clearAuth();
      router.replace("/");
      throw new Error("Session expired.");
    }

    return response;
  }

  async function loadTask() {
    setLoading(true);
    setError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/tasks/${taskId}`
      );

      const data = await safeJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(data, "Unable to load task.")
        );
      }

      setTask(data as Task);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to load task."
      );
    } finally {
      setLoading(false);
    }
  }

  async function loadProgressHistory() {
    setProgressLoading(true);
    setProgressError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/progress/task/${taskId}`
      );
      const data = await safeJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(data, "Unable to load progress history.")
        );
      }

      setProgressHistory(Array.isArray(data) ? (data as TaskProgress[]) : []);
    } catch (err) {
      setProgressError(
        err instanceof Error ? err.message : "Unable to load progress history."
      );
    } finally {
      setProgressLoading(false);
    }
  }

  function openCreateProgressModal() {
    setProgressError("");
    setSelectedProgress(null);
    setProgressForm({
      progress: String(task?.progress ?? 0),
      status: "In Progress",
      note: "",
    });
    setShowProgressModal(true);
  }

  function openEditProgressModal(item: TaskProgress) {
    setProgressError("");
    setSelectedProgress(item);
    setProgressForm({
      progress: String(item.progress),
      status: item.status || "In Progress",
      note: item.note || "",
    });
    setShowProgressModal(true);
  }

  function updateProgressForm(field: keyof ProgressForm, value: string) {
    setProgressForm((current) => ({ ...current, [field]: value }));
  }

  async function saveProgress(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setProgressError("");

    const progressValue = Number(progressForm.progress);
    if (Number.isNaN(progressValue) || progressValue < 0 || progressValue > 100) {
      setProgressError("Progress must be between 0 and 100.");
      return;
    }
    if (!progressForm.status.trim()) {
      setProgressError("Progress status is required.");
      return;
    }

    setProgressSaving(true);
    try {
      const editing = Boolean(selectedProgress);
      const response = await authenticatedFetch(
        editing
          ? `${API_BASE_URL}/api/v1/progress/${selectedProgress!.id}`
          : `${API_BASE_URL}/api/v1/progress/`,
        {
          method: editing ? "PUT" : "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(
            editing
              ? {
                  progress: Math.round(progressValue),
                  status: progressForm.status.trim(),
                  note: progressForm.note.trim() || null,
                }
              : {
                  task_id: Number(taskId),
                  progress: Math.round(progressValue),
                  status: progressForm.status.trim(),
                  note: progressForm.note.trim() || null,
                }
          ),
        }
      );
      const data = await safeJson(response);
      if (!response.ok) {
        throw new Error(getApiErrorMessage(data, "Unable to save progress."));
      }

      setShowProgressModal(false);
      setSelectedProgress(null);
      await Promise.all([loadTask(), loadProgressHistory()]);
      showSuccess(editing ? "Progress updated successfully." : "Progress added successfully.");
    } catch (err) {
      setProgressError(err instanceof Error ? err.message : "Unable to save progress.");
    } finally {
      setProgressSaving(false);
    }
  }

  async function deleteProgress() {
    if (!selectedProgress) return;
    setProgressDeleting(true);
    setProgressError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/progress/${selectedProgress.id}`,
        { method: "DELETE" }
      );
      const data = await safeJson(response);
      if (!response.ok) {
        throw new Error(getApiErrorMessage(data, "Unable to delete progress."));
      }

      setShowDeleteProgressModal(false);
      setSelectedProgress(null);
      await Promise.all([loadTask(), loadProgressHistory()]);
      showSuccess("Progress entry deleted successfully.");
    } catch (err) {
      setProgressError(err instanceof Error ? err.message : "Unable to delete progress.");
    } finally {
      setProgressDeleting(false);
    }
  }

  function openEditModal() {
    if (!task) return;

    setEditError("");
    setSuccessMessage("");

    setForm({
      name: task.name || "",
      description: task.description || "",
      project_id: String(task.project_id),

      team_id:
        task.team_id !== null &&
        task.team_id !== undefined
          ? String(task.team_id)
          : "",

      assigned_to:
        task.assigned_to !== null &&
        task.assigned_to !== undefined
          ? String(task.assigned_to)
          : "",

      status: task.status || "todo",
      priority: task.priority || "medium",

      start_date: toDateInput(task.start_date),
      due_date: toDateInput(task.due_date),
    });

    setShowEditModal(true);
  }

  function closeEditModal() {
    if (saving) return;

    setShowEditModal(false);
    setEditError("");
  }

  function updateForm(
    field: keyof TaskForm,
    value: string
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function updateTask(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setEditError("");
    setSuccessMessage("");

    if (!form.name.trim()) {
      setEditError("Task name is required.");
      return;
    }

    const projectId = Number(form.project_id);

    if (
      !Number.isInteger(projectId) ||
      projectId <= 0
    ) {
      setEditError("Valid Project ID is required.");
      return;
    }


    if (
      form.start_date &&
      form.due_date &&
      form.start_date > form.due_date
    ) {
      setEditError(
        "Start date cannot be after due date."
      );
      return;
    }

    setSaving(true);

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/tasks/${taskId}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: form.name.trim(),
            description:
              form.description.trim() || null,

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

            is_active: true,
          }),
        }
      );

      const data = await safeJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to update task."
          )
        );
      }

      setTask(data as Task);
      setShowEditModal(false);

      showSuccess("Task updated successfully.");
    } catch (err) {
      setEditError(
        err instanceof Error
          ? err.message
          : "Unable to update task."
      );
    } finally {
      setSaving(false);
    }
  }

  async function deleteTask() {
    setDeleting(true);
    setDeleteError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/tasks/${taskId}`,
        {
          method: "DELETE",
        }
      );

      const data = await safeJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to delete task."
          )
        );
      }

      router.push("/tasks");
      router.refresh();
    } catch (err) {
      setDeleteError(
        err instanceof Error
          ? err.message
          : "Unable to delete task."
      );
    } finally {
      setDeleting(false);
    }
  }

  function openCreateSubtaskModal() {
    setSubtaskError("");
    setSubtaskForm(EMPTY_SUBTASK_FORM);
    setSelectedSubtask(null);
    setShowCreateSubtaskModal(true);
  }

  function openEditSubtaskModal(subtask: Subtask) {
    setSubtaskError("");
    setSelectedSubtask(subtask);

    setSubtaskForm({
      title: subtask.title,
      description: subtask.description || "",
      status: subtask.status || "todo",
      is_active: subtask.is_active ?? true,
    });

    setShowEditSubtaskModal(true);
  }

  function openDeleteSubtaskModal(subtask: Subtask) {
    setSubtaskError("");
    setSelectedSubtask(subtask);
    setShowDeleteSubtaskModal(true);
  }

  function updateSubtaskForm(
    field: keyof SubtaskForm,
    value: string | boolean
  ) {
    setSubtaskForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function createSubtask(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!task) return;

    setSubtaskError("");

    if (!subtaskForm.title.trim()) {
      setSubtaskError("Subtask title is required.");
      return;
    }

    setSubtaskSaving(true);

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/subtasks/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: subtaskForm.title.trim(),
            description:
              subtaskForm.description.trim() || null,
            status: subtaskForm.status,
            is_active: subtaskForm.is_active,
            task_id: task.id,
          }),
        }
      );

      const data = await safeJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to create subtask."
          )
        );
      }

      const createdSubtask = data as Subtask;

      setTask((current) => {
        if (!current) return current;

        return {
          ...current,
          subtasks: [
            ...(current.subtasks || []),
            createdSubtask,
          ],
        };
      });

      setShowCreateSubtaskModal(false);
      setSubtaskForm(EMPTY_SUBTASK_FORM);

      showSuccess("Subtask created successfully.");
    } catch (err) {
      setSubtaskError(
        err instanceof Error
          ? err.message
          : "Unable to create subtask."
      );
    } finally {
      setSubtaskSaving(false);
    }
  }

  async function updateSubtask(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    if (!selectedSubtask) return;

    setSubtaskError("");

    if (!subtaskForm.title.trim()) {
      setSubtaskError("Subtask title is required.");
      return;
    }

    setSubtaskSaving(true);

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/subtasks/${selectedSubtask.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            title: subtaskForm.title.trim(),
            description:
              subtaskForm.description.trim() || null,
            status: subtaskForm.status,
            is_active: subtaskForm.is_active,
          }),
        }
      );

      const data = await safeJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to update subtask."
          )
        );
      }

      const updatedSubtask = data as Subtask;

      setTask((current) => {
        if (!current) return current;

        return {
          ...current,
          subtasks: (current.subtasks || []).map(
            (subtask) =>
              subtask.id === updatedSubtask.id
                ? updatedSubtask
                : subtask
          ),
        };
      });

      setShowEditSubtaskModal(false);
      setSelectedSubtask(null);

      showSuccess("Subtask updated successfully.");
    } catch (err) {
      setSubtaskError(
        err instanceof Error
          ? err.message
          : "Unable to update subtask."
      );
    } finally {
      setSubtaskSaving(false);
    }
  }

  async function quickChangeSubtaskStatus(
    subtask: Subtask,
    status: string
  ) {
    setSubtaskError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/subtasks/${subtask.id}`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            status,
          }),
        }
      );

      const data = await safeJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to update subtask status."
          )
        );
      }

      const updatedSubtask = data as Subtask;

      setTask((current) => {
        if (!current) return current;

        return {
          ...current,
          subtasks: (current.subtasks || []).map(
            (item) =>
              item.id === updatedSubtask.id
                ? updatedSubtask
                : item
          ),
        };
      });

      showSuccess("Subtask status updated.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to update subtask status."
      );
    }
  }

  async function deleteSubtask() {
    if (!selectedSubtask) return;

    setSubtaskDeleting(true);
    setSubtaskError("");

    try {
      const response = await authenticatedFetch(
        `${API_BASE_URL}/api/v1/subtasks/${selectedSubtask.id}`,
        {
          method: "DELETE",
        }
      );

      const data = await safeJson(response);

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to delete subtask."
          )
        );
      }

      setTask((current) => {
        if (!current) return current;

        return {
          ...current,
          subtasks: (current.subtasks || []).filter(
            (subtask) =>
              subtask.id !== selectedSubtask.id
          ),
        };
      });

      setShowDeleteSubtaskModal(false);
      setSelectedSubtask(null);

      showSuccess("Subtask deleted successfully.");
    } catch (err) {
      setSubtaskError(
        err instanceof Error
          ? err.message
          : "Unable to delete subtask."
      );
    } finally {
      setSubtaskDeleting(false);
    }
  }

  function showSuccess(message: string) {
    setSuccessMessage(message);

    window.setTimeout(() => {
      setSuccessMessage("");
    }, 3500);
  }

  function logout() {
    clearAuth();
    router.replace("/");
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />

          <p className="mt-4 text-sm font-medium text-slate-500">
            Loading task...
          </p>
        </div>
      </div>
    );
  }

  if (error || !task) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50 p-6">
        <div className="w-full max-w-md rounded-3xl border border-slate-200 bg-white p-8 text-center shadow-sm">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-xl font-bold text-red-600">
            !
          </div>

          <h1 className="mt-5 text-xl font-bold">
            Unable to open task
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            {error || "Task not found."}
          </p>

          <button
            type="button"
            onClick={() => router.push("/tasks")}
            className="mt-6 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
          >
            Back to Tasks
          </button>
        </div>
      </div>
    );
  }

  const subtasks = task.subtasks || [];

  const completedSubtasks = subtasks.filter(
    (subtask) => subtask.status === "done"
  ).length;

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-slate-800 bg-[#101828] text-white lg:flex lg:flex-col">
        <div className="flex h-20 items-center border-b border-white/10 px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold">
              T
            </div>

            <div>
              <h1 className="font-bold">
                TreeFlow AI
              </h1>

              <p className="text-xs text-slate-400">
                Smart Work Management
              </p>
            </div>
          </div>
        </div>

        <nav className="flex-1 space-y-2 p-4">
          <NavButton
            label="Dashboard"
            onClick={() =>
              router.push("/dashboard")
            }
          />

          <NavButton
            label="Projects"
            onClick={() =>
              router.push("/projects")
            }
          />

          <NavButton
            label="Tasks"
            active
            onClick={() =>
              router.push("/tasks")
            }
          />

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
        <header className="sticky top-0 z-20 flex min-h-20 items-center justify-between border-b border-slate-200 bg-white px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <button
              type="button"
              onClick={() => router.push("/tasks")}
              className="mb-1 text-sm font-semibold text-blue-600 hover:text-blue-700"
            >
              â† Back to Tasks
            </button>

            <h2 className="text-xl font-bold">
              Task Details
            </h2>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={openEditModal}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50"
            >
              Edit Task
            </button>

            <button
              type="button"
              onClick={() => {
                setDeleteError("");
                setShowDeleteModal(true);
              }}
              className="rounded-xl bg-red-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700"
            >
              Delete Task
            </button>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          {successMessage && (
            <div className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-700">
              {successMessage}
            </div>
          )}

          <section className="overflow-hidden rounded-3xl bg-[#101828] p-6 text-white shadow-lg sm:p-8">
            <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-start">
              <div>
                <p className="text-xs font-bold tracking-[0.18em] text-blue-300">
                  TASK #{task.id}
                </p>

                <h1 className="mt-3 text-3xl font-bold">
                  {task.name}
                </h1>

                <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
                  {task.description ||
                    "No description provided."}
                </p>
              </div>

              <div className="flex flex-wrap gap-2">
                <StatusBadge status={task.status} />
                <PriorityBadge
                  priority={task.priority}
                />
              </div>
            </div>
          </section>

          <section className="mt-6 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
            <InfoCard
              label="Project ID"
              value={String(task.project_id)}
            />

            <InfoCard
              label="Assigned User"
              value={
                task.assigned_to
                  ? `User #${task.assigned_to}`
                  : "Not assigned"
              }
            />

            <InfoCard
              label="Team"
              value={
                task.team_id
                  ? `Team #${task.team_id}`
                  : "Not assigned"
              }
            />

            <InfoCard
              label="Created By"
              value={`User #${task.created_by}`}
            />
          </section>

          <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <h3 className="font-bold">Task Progress</h3>
                <p className="mt-1 text-sm text-slate-500">
                  Current completion percentage with auditable progress updates.
                </p>
              </div>

              <div className="flex items-center gap-4">
                <span className="text-2xl font-bold text-blue-600">
                  {task.progress ?? 0}%
                </span>
                <button
                  type="button"
                  onClick={openCreateProgressModal}
                  className="rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                >
                  + Update Progress
                </button>
              </div>
            </div>

            <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-100">
              <div
                className="h-full rounded-full bg-blue-600 transition-all"
                style={{
                  width: `${Math.min(Math.max(task.progress ?? 0, 0), 100)}%`,
                }}
              />
            </div>
          </section>

          <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h3 className="text-lg font-bold">Progress History</h3>
                <p className="mt-1 text-sm text-slate-500">
                  Every progress update for this task, newest first.
                </p>
              </div>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-bold text-slate-600">
                {progressHistory.length} Updates
              </span>
            </div>

            {progressError && !showProgressModal && !showDeleteProgressModal && (
              <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {progressError}
              </div>
            )}

            {progressLoading ? (
              <div className="mt-6 rounded-2xl bg-slate-50 p-6 text-center text-sm font-medium text-slate-500">
                Loading progress history...
              </div>
            ) : progressHistory.length === 0 ? (
              <div className="mt-6 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-8 text-center">
                <p className="font-semibold text-slate-800">No progress updates yet</p>
                <p className="mt-1 text-sm text-slate-500">
                  Add the first update to start the task progress timeline.
                </p>
                <button
                  type="button"
                  onClick={openCreateProgressModal}
                  className="mt-4 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                >
                  Add First Update
                </button>
              </div>
            ) : (
              <div className="mt-6 space-y-3">
                {progressHistory.map((item) => (
                  <div
                    key={item.id}
                    className="rounded-2xl border border-slate-200 p-5 transition hover:border-blue-200 hover:shadow-sm"
                  >
                    <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-lg font-bold text-blue-600">{item.progress}%</span>
                          <span className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
                            {item.status}
                          </span>
                          <span className="text-xs text-slate-400">Update #{item.id}</span>
                        </div>
                        <p className="mt-2 text-sm leading-6 text-slate-600">
                          {item.note || "No note provided."}
                        </p>
                        <p className="mt-2 text-xs text-slate-400">
                          Updated {formatDateTime(item.updated_at)} by User #{item.user_id}
                        </p>
                      </div>

                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => openEditProgressModal(item)}
                          className="rounded-xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => {
                            setProgressError("");
                            setSelectedProgress(item);
                            setShowDeleteProgressModal(true);
                          }}
                          className="rounded-xl border border-red-200 px-4 py-2 text-sm font-semibold text-red-600 hover:bg-red-50"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>

          <section className="mt-6 grid gap-5 md:grid-cols-2">
            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="font-bold">
                Schedule
              </h3>

              <div className="mt-5 space-y-5">
                <DetailRow
                  label="Start Date"
                  value={formatDate(task.start_date)}
                />

                <DetailRow
                  label="Due Date"
                  value={formatDate(task.due_date)}
                />

                <DetailRow
                  label="Created"
                  value={formatDateTime(
                    task.created_at
                  )}
                />

                <DetailRow
                  label="Last Updated"
                  value={formatDateTime(
                    task.updated_at
                  )}
                />
              </div>
            </div>

            <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-bold">
                    Subtask Summary
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    Track work inside this task.
                  </p>
                </div>

                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-bold text-blue-700">
                  {completedSubtasks}/{subtasks.length} Done
                </span>
              </div>

              <div className="mt-6 grid grid-cols-3 gap-3">
                <MiniStat
                  label="Total"
                  value={subtasks.length}
                />

                <MiniStat
                  label="Done"
                  value={completedSubtasks}
                />

                <MiniStat
                  label="Open"
                  value={
                    subtasks.length -
                    completedSubtasks
                  }
                />
              </div>
            </div>
          </section>

          <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
              <div>
                <h3 className="text-lg font-bold">
                  Subtasks
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Create and manage smaller work items
                  for this task.
                </p>
              </div>

              <button
                type="button"
                onClick={openCreateSubtaskModal}
                className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
              >
                + Add Subtask
              </button>
            </div>

            {subtasks.length === 0 ? (
              <div className="mt-6 rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-10 text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-white text-xl shadow-sm">
                  âœ“
                </div>

                <h4 className="mt-4 font-bold">
                  No subtasks yet
                </h4>

                <p className="mt-1 text-sm text-slate-500">
                  Break this task into smaller,
                  manageable pieces.
                </p>

                <button
                  type="button"
                  onClick={openCreateSubtaskModal}
                  className="mt-5 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-blue-700"
                >
                  Create First Subtask
                </button>
              </div>
            ) : (
              <div className="mt-6 space-y-3">
                {subtasks.map((subtask) => (
                  <div
                    key={subtask.id}
                    className="rounded-2xl border border-slate-200 p-5 transition hover:border-blue-200 hover:shadow-sm"
                  >
                    <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-center">
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-xs font-bold text-slate-400">
                            SUBTASK #{subtask.id}
                          </span>

                          <StatusBadge
                            status={subtask.status}
                          />

                          {!subtask.is_active && (
                            <span className="rounded-full bg-red-50 px-2.5 py-1 text-xs font-semibold text-red-600">
                              Inactive
                            </span>
                          )}
                        </div>

                        <h4 className="mt-2 font-bold text-slate-900">
                          {subtask.title}
                        </h4>

                        <p className="mt-1 text-sm leading-6 text-slate-500">
                          {subtask.description ||
                            "No description provided."}
                        </p>

                        <p className="mt-2 text-xs text-slate-400">
                          Updated{" "}
                          {formatDateTime(
                            subtask.updated_at
                          )}
                        </p>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        <select
                          value={subtask.status}
                          onChange={(event) =>
                            quickChangeSubtaskStatus(
                              subtask,
                              event.target.value
                            )
                          }
                          className="h-10 rounded-xl border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700 outline-none focus:border-blue-500"
                        >
                          <option value="todo">
                            To Do
                          </option>

                          <option value="in_progress">
                            In Progress
                          </option>

                          <option value="review">
                            Review
                          </option>

                          <option value="done">
                            Done
                          </option>

                          <option value="cancelled">
                            Cancelled
                          </option>
                        </select>

                        <button
                          type="button"
                          onClick={() =>
                            openEditSubtaskModal(
                              subtask
                            )
                          }
                          className="h-10 rounded-xl border border-slate-200 px-4 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          onClick={() =>
                            openDeleteSubtaskModal(
                              subtask
                            )
                          }
                          className="h-10 rounded-xl border border-red-200 px-4 text-sm font-semibold text-red-600 hover:bg-red-50"
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </main>
      </div>

      {showCreateSubtaskModal && (
        <ModalShell
          title="Create Subtask"
          description="Add a smaller work item to this task."
          onClose={() => {
            if (!subtaskSaving) {
              setShowCreateSubtaskModal(false);
              setSubtaskError("");
            }
          }}
        >
          <SubtaskFormContent
            form={subtaskForm}
            error={subtaskError}
            saving={subtaskSaving}
            submitLabel="Create Subtask"
            onChange={updateSubtaskForm}
            onSubmit={createSubtask}
            onCancel={() =>
              setShowCreateSubtaskModal(false)
            }
          />
        </ModalShell>
      )}

      {showEditSubtaskModal &&
        selectedSubtask && (
          <ModalShell
            title="Edit Subtask"
            description={`Update Subtask #${selectedSubtask.id}.`}
            onClose={() => {
              if (!subtaskSaving) {
                setShowEditSubtaskModal(false);
                setSelectedSubtask(null);
                setSubtaskError("");
              }
            }}
          >
            <SubtaskFormContent
              form={subtaskForm}
              error={subtaskError}
              saving={subtaskSaving}
              submitLabel="Save Changes"
              onChange={updateSubtaskForm}
              onSubmit={updateSubtask}
              onCancel={() => {
                setShowEditSubtaskModal(false);
                setSelectedSubtask(null);
              }}
            />
          </ModalShell>
        )}

      {showDeleteSubtaskModal &&
        selectedSubtask && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-red-50 text-xl font-bold text-red-600">
                !
              </div>

              <h2 className="mt-5 text-xl font-bold">
                Delete Subtask?
              </h2>

              <p className="mt-2 text-sm leading-6 text-slate-500">
                Are you sure you want to delete{" "}
                <span className="font-semibold text-slate-800">
                  {selectedSubtask.title}
                </span>
                ?
              </p>

              {subtaskError && (
                <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                  {subtaskError}
                </div>
              )}

              <div className="mt-6 flex justify-end gap-3">
                <button
                  type="button"
                  disabled={subtaskDeleting}
                  onClick={() => {
                    setShowDeleteSubtaskModal(false);
                    setSelectedSubtask(null);
                    setSubtaskError("");
                  }}
                  className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  disabled={subtaskDeleting}
                  onClick={deleteSubtask}
                  className="rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60"
                >
                  {subtaskDeleting
                    ? "Deleting..."
                    : "Delete Subtask"}
                </button>
              </div>
            </div>
          </div>
        )}

      {showProgressModal && (
        <ModalShell
          title={selectedProgress ? "Edit Progress" : "Update Progress"}
          description={
            selectedProgress
              ? `Update Progress #${selectedProgress.id}.`
              : "Add a new progress update to this task."
          }
          onClose={() => {
            if (!progressSaving) {
              setShowProgressModal(false);
              setSelectedProgress(null);
              setProgressError("");
            }
          }}
        >
          <form onSubmit={saveProgress}>
            {progressError && (
              <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
                {progressError}
              </div>
            )}

            <div className="space-y-5">
              <div>
                <div className="flex items-center justify-between">
                  <label className={labelClass}>Progress *</label>
                  <span className="text-lg font-bold text-blue-600">
                    {progressForm.progress}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={progressForm.progress}
                  onChange={(event) => updateProgressForm("progress", event.target.value)}
                  className="mt-2 w-full accent-blue-600"
                />
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={progressForm.progress}
                  onChange={(event) => updateProgressForm("progress", event.target.value)}
                  className={`${inputClass} mt-3`}
                />
              </div>

              <div>
                <label className={labelClass}>Status *</label>
                <select
                  value={progressForm.status}
                  onChange={(event) => updateProgressForm("status", event.target.value)}
                  className={inputClass}
                >
                  <option value="In Progress">In Progress</option>
                  <option value="Review">Review</option>
                  <option value="Completed">Completed</option>
                  <option value="Blocked">Blocked</option>
                  <option value="On Hold">On Hold</option>
                </select>
              </div>

              <div>
                <label className={labelClass}>Note</label>
                <textarea
                  rows={4}
                  value={progressForm.note}
                  onChange={(event) => updateProgressForm("note", event.target.value)}
                  placeholder="What changed in this progress update?"
                  className={`${inputClass} h-auto resize-none py-3`}
                />
              </div>
            </div>

            <div className="mt-7 flex justify-end gap-3 border-t border-slate-100 pt-5">
              <button
                type="button"
                disabled={progressSaving}
                onClick={() => {
                  setShowProgressModal(false);
                  setSelectedProgress(null);
                  setProgressError("");
                }}
                className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={progressSaving}
                className="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
              >
                {progressSaving
                  ? "Saving..."
                  : selectedProgress
                  ? "Save Progress"
                  : "Add Progress"}
              </button>
            </div>
          </form>
        </ModalShell>
      )}

      {showDeleteProgressModal && selectedProgress && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-red-50 text-xl font-bold text-red-600">
              !
            </div>
            <h2 className="mt-5 text-xl font-bold">Delete Progress Update?</h2>
            <p className="mt-2 text-sm leading-6 text-slate-500">
              Delete progress update #{selectedProgress.id} ({selectedProgress.progress}%)?
              The task will automatically sync to the latest remaining progress entry, or 0% if none remain.
            </p>

            {progressError && (
              <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {progressError}
              </div>
            )}

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                disabled={progressDeleting}
                onClick={() => {
                  setShowDeleteProgressModal(false);
                  setSelectedProgress(null);
                  setProgressError("");
                }}
                className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={progressDeleting}
                onClick={deleteProgress}
                className="rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60"
              >
                {progressDeleting ? "Deleting..." : "Delete Progress"}
              </button>
            </div>
          </div>
        </div>
      )}

      {showEditModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
          <div className="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white shadow-2xl">
            <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-5">
              <div>
                <h2 className="text-xl font-bold">
                  Edit Task
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Update task information.
                </p>
              </div>

              <button
                type="button"
                onClick={closeEditModal}
                disabled={saving}
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-xl text-slate-500 hover:bg-slate-200"
              >
                Ã—
              </button>
            </div>

            <form
              onSubmit={updateTask}
              className="p-6"
            >
              {editError && (
                <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
                  {editError}
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
                      updateForm(
                        "name",
                        event.target.value
                      )
                    }
                    className={inputClass}
                    required
                  />
                </div>

                <div className="sm:col-span-2">
                  <label className={labelClass}>
                    Description
                  </label>

                  <textarea
                    rows={4}
                    value={form.description}
                    onChange={(event) =>
                      updateForm(
                        "description",
                        event.target.value
                      )
                    }
                    className={`${inputClass} h-auto resize-none py-3`}
                  />
                </div>

                <div>
                  <label className={labelClass}>
                    Project ID *
                  </label>

                  <input
                    type="number"
                    min="1"
                    value={form.project_id}
                    onChange={(event) =>
                      updateForm(
                        "project_id",
                        event.target.value
                      )
                    }
                    className={inputClass}
                    required
                  />
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
                      updateForm(
                        "assigned_to",
                        event.target.value
                      )
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
                      updateForm(
                        "team_id",
                        event.target.value
                      )
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
                      updateForm(
                        "status",
                        event.target.value
                      )
                    }
                    className={inputClass}
                  >
                    <option value="todo">
                      To Do
                    </option>

                    <option value="in_progress">
                      In Progress
                    </option>

                    <option value="review">
                      Review
                    </option>

                    <option value="done">
                      Done
                    </option>

                    <option value="cancelled">
                      Cancelled
                    </option>
                  </select>
                </div>

                <div>
                  <label className={labelClass}>
                    Priority
                  </label>

                  <select
                    value={form.priority}
                    onChange={(event) =>
                      updateForm(
                        "priority",
                        event.target.value
                      )
                    }
                    className={inputClass}
                  >
                    <option value="low">
                      Low
                    </option>

                    <option value="medium">
                      Medium
                    </option>

                    <option value="high">
                      High
                    </option>

                    <option value="critical">
                      Critical
                    </option>
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
                      updateForm(
                        "start_date",
                        event.target.value
                      )
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
                      updateForm(
                        "due_date",
                        event.target.value
                      )
                    }
                    className={inputClass}
                  />
                </div>

                <div className="sm:col-span-2 rounded-xl border border-blue-100 bg-blue-50 p-4">
                  <p className="text-sm font-semibold text-blue-800">
                    Progress is managed from the dedicated Progress Tracking section.
                  </p>
                </div>
              </div>

              <div className="mt-7 flex justify-end gap-3 border-t border-slate-100 pt-5">
                <button
                  type="button"
                  onClick={closeEditModal}
                  disabled={saving}
                  className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={saving}
                  className="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
                >
                  {saving
                    ? "Saving..."
                    : "Save Changes"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDeleteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-red-50 text-xl font-bold text-red-600">
              !
            </div>

            <h2 className="mt-5 text-xl font-bold">
              Delete Task?
            </h2>

            <p className="mt-2 text-sm leading-6 text-slate-500">
              Are you sure you want to delete{" "}
              <span className="font-semibold text-slate-800">
                {task.name}
              </span>
              ?
            </p>

            {deleteError && (
              <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {deleteError}
              </div>
            )}

            <div className="mt-6 flex justify-end gap-3">
              <button
                type="button"
                disabled={deleting}
                onClick={() =>
                  setShowDeleteModal(false)
                }
                className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700"
              >
                Cancel
              </button>

              <button
                type="button"
                disabled={deleting}
                onClick={deleteTask}
                className="rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-60"
              >
                {deleting
                  ? "Deleting..."
                  : "Delete Task"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SubtaskFormContent({
  form,
  error,
  saving,
  submitLabel,
  onChange,
  onSubmit,
  onCancel,
}: {
  form: SubtaskForm;
  error: string;
  saving: boolean;
  submitLabel: string;
  onChange: (
    field: keyof SubtaskForm,
    value: string | boolean
  ) => void;
  onSubmit: (
    event: FormEvent<HTMLFormElement>
  ) => void;
  onCancel: () => void;
}) {
  return (
    <form onSubmit={onSubmit}>
      {error && (
        <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
          {error}
        </div>
      )}

      <div className="space-y-5">
        <div>
          <label className={labelClass}>
            Subtask Title *
          </label>

          <input
            type="text"
            value={form.title}
            onChange={(event) =>
              onChange(
                "title",
                event.target.value
              )
            }
            placeholder="Enter subtask title"
            className={inputClass}
            required
          />
        </div>

        <div>
          <label className={labelClass}>
            Description
          </label>

          <textarea
            rows={4}
            value={form.description}
            onChange={(event) =>
              onChange(
                "description",
                event.target.value
              )
            }
            placeholder="Describe this subtask..."
            className={`${inputClass} h-auto resize-none py-3`}
          />
        </div>

        <div>
          <label className={labelClass}>
            Status
          </label>

          <select
            value={form.status}
            onChange={(event) =>
              onChange(
                "status",
                event.target.value
              )
            }
            className={inputClass}
          >
            <option value="todo">
              To Do
            </option>

            <option value="in_progress">
              In Progress
            </option>

            <option value="review">
              Review
            </option>

            <option value="done">
              Done
            </option>

            <option value="cancelled">
              Cancelled
            </option>
          </select>
        </div>

        <label className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 p-4">
          <input
            type="checkbox"
            checked={form.is_active}
            onChange={(event) =>
              onChange(
                "is_active",
                event.target.checked
              )
            }
            className="h-4 w-4 accent-blue-600"
          />

          <div>
            <p className="text-sm font-semibold">
              Active Subtask
            </p>

            <p className="text-xs text-slate-500">
              Keep this subtask active in the
              workflow.
            </p>
          </div>
        </label>
      </div>

      <div className="mt-7 flex justify-end gap-3 border-t border-slate-100 pt-5">
        <button
          type="button"
          disabled={saving}
          onClick={onCancel}
          className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700"
        >
          Cancel
        </button>

        <button
          type="submit"
          disabled={saving}
          className="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-60"
        >
          {saving
            ? "Saving..."
            : submitLabel}
        </button>
      </div>
    </form>
  );
}

function ModalShell({
  title,
  description,
  onClose,
  children,
}: {
  title: string;
  description: string;
  onClose: () => void;
  children: React.ReactNode;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
      <div className="max-h-[92vh] w-full max-w-xl overflow-y-auto rounded-3xl bg-white shadow-2xl">
        <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-5">
          <div>
            <h2 className="text-xl font-bold">
              {title}
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              {description}
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-xl text-slate-500 hover:bg-slate-200"
          >
            Ã—
          </button>
        </div>

        <div className="p-6">
          {children}
        </div>
      </div>
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

function InfoCard({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-2 font-bold text-slate-800">
        {value}
      </p>
    </div>
  );
}

function MiniStat({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-xl bg-slate-50 p-4 text-center">
      <p className="text-xl font-bold text-slate-900">
        {value}
      </p>

      <p className="mt-1 text-xs font-semibold text-slate-500">
        {label}
      </p>
    </div>
  );
}

function DetailRow({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-4 last:border-0 last:pb-0">
      <span className="text-sm text-slate-500">
        {label}
      </span>

      <span className="text-right text-sm font-semibold text-slate-800">
        {value}
      </span>
    </div>
  );
}

function StatusBadge({
  status,
}: {
  status: string;
}) {
  const normalized = status.toLowerCase();

  let classes =
    "bg-slate-100 text-slate-700";

  if (normalized === "done") {
    classes =
      "bg-emerald-100 text-emerald-700";
  } else if (
    normalized === "in_progress"
  ) {
    classes =
      "bg-blue-100 text-blue-700";
  } else if (normalized === "review") {
    classes =
      "bg-amber-100 text-amber-700";
  } else if (
    normalized === "cancelled"
  ) {
    classes =
      "bg-red-100 text-red-700";
  }

  return (
    <span
      className={`rounded-full px-3 py-1.5 text-xs font-bold ${classes}`}
    >
      {formatLabel(status)}
    </span>
  );
}

function PriorityBadge({
  priority,
}: {
  priority: string;
}) {
  const normalized = priority.toLowerCase();

  let classes =
    "bg-slate-100 text-slate-700";

  if (normalized === "critical") {
    classes =
      "bg-red-100 text-red-700";
  } else if (normalized === "high") {
    classes =
      "bg-orange-100 text-orange-700";
  } else if (normalized === "medium") {
    classes =
      "bg-amber-100 text-amber-700";
  } else if (normalized === "low") {
    classes =
      "bg-emerald-100 text-emerald-700";
  }

  return (
    <span
      className={`rounded-full px-3 py-1.5 text-xs font-bold ${classes}`}
    >
      {formatLabel(priority)}
    </span>
  );
}

function formatLabel(value: string) {
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) =>
      letter.toUpperCase()
    );
}

function toDateInput(
  value?: string | null
) {
  if (!value) return "";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "";
  }

  return date.toISOString().slice(0, 10);
}

function formatDate(
  value?: string | null
) {
  if (!value) return "Not set";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }
  ).format(date);
}

function formatDateTime(
  value?: string | null
) {
  if (!value) return "Not available";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat(
    "en-IN",
    {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }
  ).format(date);
}

async function safeJson(
  response: Response
): Promise<unknown> {
  try {
    return await response.json();
  } catch {
    return null;
  }
}

function getApiErrorMessage(
  data: unknown,
  fallback: string
) {
  if (
    typeof data === "object" &&
    data !== null &&
    "detail" in data
  ) {
    const detail = (
      data as {
        detail?: unknown;
      }
    ).detail;

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
              (
                item as {
                  msg?: unknown;
                }
              ).msg || ""
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
