"use client";

import {
  FormEvent,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = "http://127.0.0.1:8000";

type Project = {
  id: number;
  name: string;
  description?: string | null;
  company_id?: number;
  department_id?: number | null;
  team_id?: number | null;
  created_by?: number;
  start_date?: string | null;
  end_date?: string | null;
  status?: string;
  progress?: number;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
};

type ProjectForm = {
  name: string;
  description: string;
  company_id: string;
  department_id: string;
  team_id: string;
  status: string;
  start_date: string;
  end_date: string;
  progress: string;
};

const EMPTY_FORM: ProjectForm = {
  name: "",
  description: "",
  company_id: "2",
  department_id: "",
  team_id: "",
  status: "Planned",
  start_date: "",
  end_date: "",
  progress: "0",
};

export default function ProjectsPage() {
  const router = useRouter();

  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const [showCreateModal, setShowCreateModal] =
    useState(false);

  const [form, setForm] =
    useState<ProjectForm>(EMPTY_FORM);

  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const [successMessage, setSuccessMessage] =
    useState("");

  useEffect(() => {
    loadProjects();
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

  async function loadProjects() {
    setLoading(true);
    setError("");

    try {
      const token = getToken();

      if (!token) {
        clearAuth();
        router.replace("/");
        return;
      }

      const response = await fetch(
        `${API_BASE_URL}/api/v1/projects/`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
          cache: "no-store",
        }
      );

      if (response.status === 401) {
        clearAuth();
        router.replace("/");
        return;
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to load projects."
          )
        );
      }

      setProjects(
        Array.isArray(data) ? data : []
      );
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to load projects.");
      }
    } finally {
      setLoading(false);
    }
  }

  function openCreateModal() {
    setForm(EMPTY_FORM);
    setCreateError("");
    setSuccessMessage("");
    setShowCreateModal(true);
  }

  function closeCreateModal() {
    if (creating) {
      return;
    }

    setShowCreateModal(false);
    setCreateError("");
    setForm(EMPTY_FORM);
  }

  function updateForm(
    field: keyof ProjectForm,
    value: string
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function createProject(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setCreateError("");
    setSuccessMessage("");

    if (!form.name.trim()) {
      setCreateError(
        "Project name is required."
      );
      return;
    }

    const companyId =
      Number(form.company_id);

    if (
      !form.company_id.trim() ||
      !Number.isInteger(companyId) ||
      companyId <= 0
    ) {
      setCreateError(
        "Please enter a valid Company ID."
      );
      return;
    }

    const progress = Number(form.progress);

    if (
      Number.isNaN(progress) ||
      progress < 0 ||
      progress > 100
    ) {
      setCreateError(
        "Progress must be between 0 and 100."
      );
      return;
    }

    if (
      form.start_date &&
      form.end_date &&
      form.start_date > form.end_date
    ) {
      setCreateError(
        "Start date cannot be after end date."
      );
      return;
    }

    setCreating(true);

    try {
      const token = getToken();

      if (!token) {
        clearAuth();
        router.replace("/");
        return;
      }

      const payload = {
        name: form.name.trim(),

        description:
          form.description.trim() || null,

        company_id: companyId,

        department_id:
          form.department_id.trim()
            ? Number(form.department_id)
            : null,

        team_id:
          form.team_id.trim()
            ? Number(form.team_id)
            : null,

        status: form.status,

        start_date:
          form.start_date
            ? `${form.start_date}T00:00:00`
            : null,

        end_date:
          form.end_date
            ? `${form.end_date}T23:59:59`
            : null,

        progress: Math.round(progress),

        is_active: true,
      };

      const response = await fetch(
        `${API_BASE_URL}/api/v1/projects/`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
            Accept: "application/json",
          },
          body: JSON.stringify(payload),
        }
      );

      if (response.status === 401) {
        clearAuth();
        router.replace("/");
        return;
      }

      let data: unknown = null;

      try {
        data = await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to create project."
          )
        );
      }

      setShowCreateModal(false);
      setForm(EMPTY_FORM);

      setSuccessMessage(
        "Project created successfully."
      );

      await loadProjects();

      window.setTimeout(() => {
        setSuccessMessage("");
      }, 4000);
    } catch (err) {
      if (err instanceof Error) {
        setCreateError(err.message);
      } else {
        setCreateError(
          "Unable to create project."
        );
      }
    } finally {
      setCreating(false);
    }
  }

  function logout() {
    clearAuth();
    router.replace("/");
  }

  const filteredProjects = useMemo(() => {
    const query =
      search.trim().toLowerCase();

    if (!query) {
      return projects;
    }

    return projects.filter((project) => {
      return (
        project.name
          ?.toLowerCase()
          .includes(query) ||
        project.description
          ?.toLowerCase()
          .includes(query) ||
        project.status
          ?.toLowerCase()
          .includes(query)
      );
    });
  }, [projects, search]);

  const completedCount =
    projects.filter(
      (project) =>
        project.status?.toLowerCase() ===
        "completed"
    ).length;

  const inProgressCount =
    projects.filter(
      (project) =>
        project.status?.toLowerCase() ===
        "in progress"
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
            active
            onClick={() =>
              router.push("/projects")
            }
          />

          <NavButton
            label="Tasks"
            onClick={() => router.push("/tasks")}
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
        <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-slate-200 bg-white px-4 sm:px-6 lg:px-8">
          <div>
            <h2 className="text-xl font-bold">
              Projects
            </h2>

            <p className="text-sm text-slate-500">
              Manage and monitor your accessible
              projects.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={loadProjects}
              disabled={loading}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            >
              {loading
                ? "Refreshing..."
                : "Refresh"}
            </button>

            <button
              type="button"
              onClick={openCreateModal}
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
            >
              + New Project
            </button>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          <section className="mb-8 rounded-3xl bg-[#101828] p-6 text-white sm:p-8">
            <p className="text-xs font-bold tracking-[0.18em] text-blue-300">
              PROJECT WORKSPACE
            </p>

            <h1 className="mt-3 text-3xl font-bold">
              Your Projects
            </h1>

            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
              Track project status, progress and
              timelines from one centralized workspace.
            </p>
          </section>

          {successMessage && (
            <div className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-700">
              {successMessage}
            </div>
          )}

          {error && (
            <div className="mb-6 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              {error}
            </div>
          )}

          <section className="grid gap-4 sm:grid-cols-3">
            <StatCard
              label="Total Projects"
              value={projects.length}
            />

            <StatCard
              label="In Progress"
              value={inProgressCount}
            />

            <StatCard
              label="Completed"
              value={completedCount}
            />
          </section>

          <section className="mt-8">
            <div className="mb-5 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <h3 className="text-lg font-bold">
                  Project List
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  {filteredProjects.length} project
                  {filteredProjects.length === 1
                    ? ""
                    : "s"}{" "}
                  found
                </p>
              </div>

              <div className="flex w-full flex-col gap-3 sm:w-auto sm:flex-row">
                <input
                  type="search"
                  value={search}
                  onChange={(event) =>
                    setSearch(event.target.value)
                  }
                  placeholder="Search projects..."
                  className="h-11 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 sm:w-72"
                />

                <button
                  type="button"
                  onClick={openCreateModal}
                  className="h-11 rounded-xl bg-blue-600 px-5 text-sm font-semibold text-white transition hover:bg-blue-700"
                >
                  + New Project
                </button>
              </div>
            </div>

            {loading ? (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                <ProjectSkeleton />
                <ProjectSkeleton />
                <ProjectSkeleton />
              </div>
            ) : filteredProjects.length > 0 ? (
              <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
                {filteredProjects.map((project) => (
                  <ProjectCard
                    key={project.id}
                    project={project}
                  />
                ))}
              </div>
            ) : (
              <div className="rounded-2xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-50 text-xl font-bold text-blue-600">
                  P
                </div>

                <h3 className="mt-4 font-bold">
                  No projects found
                </h3>

                <p className="mt-2 text-sm text-slate-500">
                  Create your first project to start
                  managing work in TreeFlow AI.
                </p>

                <button
                  type="button"
                  onClick={openCreateModal}
                  className="mt-5 rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700"
                >
                  Create Project
                </button>
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
                  Create New Project
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Add a new project to TreeFlow AI.
                </p>
              </div>

              <button
                type="button"
                onClick={closeCreateModal}
                disabled={creating}
                className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-xl text-slate-500 transition hover:bg-slate-200"
              >
                ×
              </button>
            </div>

            <form
              onSubmit={createProject}
              className="p-6"
            >
              {createError && (
                <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
                  {createError}
                </div>
              )}

              <div className="grid gap-5 sm:grid-cols-2">
                <div className="sm:col-span-2">
                  <label className={labelClass}>
                    Project Name *
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
                    placeholder="TreeFlow Test Project"
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
                      updateForm(
                        "description",
                        event.target.value
                      )
                    }
                    rows={4}
                    placeholder="Project description..."
                    className={`${inputClass} h-auto resize-none py-3`}
                  />
                </div>

                <div>
                  <label className={labelClass}>
                    Company ID *
                  </label>

                  <input
                    type="number"
                    min="1"
                    value={form.company_id}
                    onChange={(event) =>
                      updateForm(
                        "company_id",
                        event.target.value
                      )
                    }
                    className={inputClass}
                    required
                  />
                </div>

                <div>
                  <label className={labelClass}>
                    Department ID
                  </label>

                  <input
                    type="number"
                    min="1"
                    value={form.department_id}
                    onChange={(event) =>
                      updateForm(
                        "department_id",
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
                    <option value="Planned">
                      Planned
                    </option>

                    <option value="In Progress">
                      In Progress
                    </option>

                    <option value="On Hold">
                      On Hold
                    </option>

                    <option value="Completed">
                      Completed
                    </option>

                    <option value="Cancelled">
                      Cancelled
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
                    End Date
                  </label>

                  <input
                    type="date"
                    value={form.end_date}
                    onChange={(event) =>
                      updateForm(
                        "end_date",
                        event.target.value
                      )
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
                    value={form.progress}
                    onChange={(event) =>
                      updateForm(
                        "progress",
                        event.target.value
                      )
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
                  className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={creating}
                  className="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
                >
                  {creating
                    ? "Creating..."
                    : "Create Project"}
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

      <p className="mt-2 text-3xl font-bold">
        {value}
      </p>
    </div>
  );
}

function ProjectCard({
  project,
}: {
  project: Project;
}) {
  const router = useRouter();

  return (
    <button
      type="button"
      onClick={() =>
        router.push(`/projects/${project.id}`)
      }
      className="w-full text-left"
    >
      <article className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-1 hover:border-blue-200 hover:shadow-lg">
        <div className="flex items-start justify-between gap-4">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 font-bold text-blue-600">
            {project.name
              ?.charAt(0)
              ?.toUpperCase() || "P"}
          </div>

          <StatusBadge
            status={
              project.status || "Unknown"
            }
          />
        </div>

        <h3 className="mt-5 text-lg font-bold">
          {project.name}
        </h3>

        <p className="mt-2 min-h-10 text-sm leading-5 text-slate-500">
          {project.description ||
            "No description available."}
        </p>

        <div className="mt-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-500">
              Progress
            </span>

            <span className="text-xs font-bold">
              {project.progress ?? 0}%
            </span>
          </div>

          <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-blue-600"
              style={{
                width: `${Math.min(
                  Math.max(
                    project.progress ?? 0,
                    0
                  ),
                  100
                )}%`,
              }}
            />
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-4 border-t border-slate-100 pt-4">
          <div>
            <p className="text-[11px] font-semibold uppercase text-slate-400">
              Start
            </p>

            <p className="mt-1 text-xs font-medium">
              {formatDate(project.start_date)}
            </p>
          </div>

          <div>
            <p className="text-[11px] font-semibold uppercase text-slate-400">
              End
            </p>

            <p className="mt-1 text-xs font-medium">
              {formatDate(project.end_date)}
            </p>
          </div>
        </div>

        <p className="mt-5 text-xs font-semibold text-blue-600">
          View Project →
        </p>
      </article>
    </button>
  );
}

function StatusBadge({
  status,
}: {
  status: string;
}) {
  const normalized =
    status.toLowerCase();

  let classes =
    "bg-slate-100 text-slate-600";

  if (normalized === "completed") {
    classes =
      "bg-emerald-50 text-emerald-700";
  } else if (
    normalized === "in progress"
  ) {
    classes =
      "bg-blue-50 text-blue-700";
  } else if (
    normalized === "planned"
  ) {
    classes =
      "bg-violet-50 text-violet-700";
  } else if (
    normalized === "on hold"
  ) {
    classes =
      "bg-amber-50 text-amber-700";
  } else if (
    normalized === "cancelled"
  ) {
    classes =
      "bg-red-50 text-red-700";
  }

  return (
    <span
      className={`rounded-full px-3 py-1 text-[11px] font-semibold ${classes}`}
    >
      {status}
    </span>
  );
}

function ProjectSkeleton() {
  return (
    <div className="animate-pulse rounded-2xl border border-slate-200 bg-white p-5">
      <div className="h-11 w-11 rounded-xl bg-slate-100" />
      <div className="mt-5 h-5 w-1/2 rounded bg-slate-100" />
      <div className="mt-3 h-4 w-full rounded bg-slate-100" />
      <div className="mt-2 h-4 w-4/5 rounded bg-slate-100" />
      <div className="mt-6 h-2 rounded-full bg-slate-100" />
    </div>
  );
}

function formatDate(
  value?: string | null
) {
  if (!value) {
    return "Not set";
  }

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
