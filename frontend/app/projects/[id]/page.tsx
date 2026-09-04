"use client";

import {
  FormEvent,
  useEffect,
  useState,
} from "react";
import {
  useParams,
  useRouter,
} from "next/navigation";

const API_BASE_URL =
  "http://127.0.0.1:8000";

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

type EditForm = {
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

export default function ProjectDetailsPage() {
  const router = useRouter();
  const params = useParams();

  const projectId = params.id as string;

  const [project, setProject] =
    useState<Project | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [showEditModal, setShowEditModal] =
    useState(false);

  const [showDeleteModal, setShowDeleteModal] =
    useState(false);

  const [saving, setSaving] =
    useState(false);

  const [deleting, setDeleting] =
    useState(false);

  const [editError, setEditError] =
    useState("");

  const [deleteError, setDeleteError] =
    useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  const [form, setForm] =
    useState<EditForm>({
      name: "",
      description: "",
      company_id: "",
      department_id: "",
      team_id: "",
      status: "Planned",
      start_date: "",
      end_date: "",
      progress: "0",
    });

  useEffect(() => {
    loadProject();
  }, [projectId]);

  function getToken() {
    if (
      typeof window === "undefined"
    ) {
      return null;
    }

    return (
      localStorage.getItem(
        "treeflow_access_token"
      ) ||
      sessionStorage.getItem(
        "treeflow_access_token"
      )
    );
  }

  function clearAuth() {
    localStorage.removeItem(
      "treeflow_access_token"
    );
    localStorage.removeItem(
      "treeflow_token_type"
    );

    sessionStorage.removeItem(
      "treeflow_access_token"
    );
    sessionStorage.removeItem(
      "treeflow_token_type"
    );
  }

  async function loadProject() {
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
        `${API_BASE_URL}/api/v1/projects/${projectId}`,
        {
          method: "GET",
          headers: {
            Authorization:
              `Bearer ${token}`,
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

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data?.detail ===
            "string"
            ? data.detail
            : "Unable to load project."
        );
      }

      setProject(data);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to load project."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  function openEditModal() {
    if (!project) {
      return;
    }

    setEditError("");
    setSuccessMessage("");

    setForm({
      name:
        project.name || "",

      description:
        project.description || "",

      company_id:
        project.company_id
          ? String(project.company_id)
          : "",

      department_id:
        project.department_id
          ? String(
              project.department_id
            )
          : "",

      team_id:
        project.team_id
          ? String(project.team_id)
          : "",

      status:
        project.status ||
        "Planned",

      start_date:
        toInputDate(
          project.start_date
        ),

      end_date:
        toInputDate(
          project.end_date
        ),

      progress:
        String(
          project.progress ?? 0
        ),
    });

    setShowEditModal(true);
  }

  function closeEditModal() {
    if (saving) {
      return;
    }

    setShowEditModal(false);
    setEditError("");
  }

  function openDeleteModal() {
    setDeleteError("");
    setShowDeleteModal(true);
  }

  function closeDeleteModal() {
    if (deleting) {
      return;
    }

    setShowDeleteModal(false);
    setDeleteError("");
  }

  function updateForm(
    field: keyof EditForm,
    value: string
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function updateProject(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setEditError("");
    setSuccessMessage("");

    if (!form.name.trim()) {
      setEditError(
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
      setEditError(
        "Please enter a valid Company ID."
      );
      return;
    }

    const progress =
      Number(form.progress);

    if (
      Number.isNaN(progress) ||
      progress < 0 ||
      progress > 100
    ) {
      setEditError(
        "Progress must be between 0 and 100."
      );
      return;
    }

    if (
      form.start_date &&
      form.end_date &&
      form.start_date >
        form.end_date
    ) {
      setEditError(
        "Start date cannot be after end date."
      );
      return;
    }

    setSaving(true);

    try {
      const token = getToken();

      if (!token) {
        clearAuth();
        router.replace("/");
        return;
      }

      const payload = {
        name:
          form.name.trim(),

        description:
          form.description.trim() ||
          null,

        company_id:
          companyId,

        department_id:
          form.department_id.trim()
            ? Number(
                form.department_id
              )
            : null,

        team_id:
          form.team_id.trim()
            ? Number(
                form.team_id
              )
            : null,

        status:
          form.status,

        start_date:
          form.start_date
            ? `${form.start_date}T00:00:00`
            : null,

        end_date:
          form.end_date
            ? `${form.end_date}T23:59:59`
            : null,

        progress:
          Math.round(progress),

        is_active:
          project?.is_active ??
          true,
      };

      const response = await fetch(
        `${API_BASE_URL}/api/v1/projects/${projectId}`,
        {
          method: "PUT",
          headers: {
            Authorization:
              `Bearer ${token}`,
            "Content-Type":
              "application/json",
            Accept:
              "application/json",
          },
          body:
            JSON.stringify(payload),
        }
      );

      if (response.status === 401) {
        clearAuth();
        router.replace("/");
        return;
      }

      let data: unknown = null;

      try {
        data =
          await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to update project."
          )
        );
      }

      setShowEditModal(false);

      setSuccessMessage(
        "Project updated successfully."
      );

      await loadProject();

      window.setTimeout(() => {
        setSuccessMessage("");
      }, 4000);
    } catch (err) {
      if (err instanceof Error) {
        setEditError(
          err.message
        );
      } else {
        setEditError(
          "Unable to update project."
        );
      }
    } finally {
      setSaving(false);
    }
  }

  async function deleteProject() {
    setDeleting(true);
    setDeleteError("");

    try {
      const token = getToken();

      if (!token) {
        clearAuth();
        router.replace("/");
        return;
      }

      const response = await fetch(
        `${API_BASE_URL}/api/v1/projects/${projectId}`,
        {
          method: "DELETE",
          headers: {
            Authorization:
              `Bearer ${token}`,
            Accept:
              "application/json",
          },
        }
      );

      if (response.status === 401) {
        clearAuth();
        router.replace("/");
        return;
      }

      let data: unknown = null;

      try {
        data =
          await response.json();
      } catch {
        data = null;
      }

      if (!response.ok) {
        throw new Error(
          getApiErrorMessage(
            data,
            "Unable to delete project."
          )
        );
      }

      setShowDeleteModal(false);

      router.replace("/projects");
      router.refresh();
    } catch (err) {
      if (err instanceof Error) {
        setDeleteError(
          err.message
        );
      } else {
        setDeleteError(
          "Unable to delete project."
        );
      }
    } finally {
      setDeleting(false);
    }
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
              router.push(
                "/dashboard"
              )
            }
          />

          <NavButton
            label="Projects"
            active
            onClick={() =>
              router.push(
                "/projects"
              )
            }
          />

          <NavButton label="Tasks" />
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
            <button
              type="button"
              onClick={() =>
                router.push(
                  "/projects"
                )
              }
              className="text-sm font-semibold text-blue-600 hover:text-blue-700"
            >
              ← Back to Projects
            </button>

            <h2 className="mt-1 text-xl font-bold">
              Project Details
            </h2>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <button
              type="button"
              onClick={loadProject}
              disabled={loading}
              className="rounded-xl border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
            >
              Refresh
            </button>

            <button
              type="button"
              onClick={openEditModal}
              disabled={
                !project ||
                loading
              }
              className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
            >
              Edit Project
            </button>

            <button
              type="button"
              onClick={openDeleteModal}
              disabled={
                !project ||
                loading
              }
              className="rounded-xl bg-red-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-60"
            >
              Delete Project
            </button>
          </div>
        </header>

        <main className="p-4 sm:p-6 lg:p-8">
          {successMessage && (
            <div className="mb-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold text-emerald-700">
              {successMessage}
            </div>
          )}

          {loading && (
            <div className="rounded-3xl border border-slate-200 bg-white p-10 text-center shadow-sm">
              <p className="text-sm font-semibold text-slate-500">
                Loading project...
              </p>
            </div>
          )}

          {error &&
            !loading && (
              <div className="rounded-2xl border border-red-200 bg-red-50 p-5 text-sm font-medium text-red-700">
                {error}
              </div>
            )}

          {project &&
            !loading && (
              <>
                <section className="rounded-3xl bg-[#101828] p-6 text-white sm:p-8">
                  <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <p className="text-xs font-bold tracking-[0.18em] text-blue-300">
                        PROJECT #
                        {project.id}
                      </p>

                      <h1 className="mt-3 text-3xl font-bold">
                        {project.name}
                      </h1>

                      <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
                        {project.description ||
                          "No description available for this project."}
                      </p>
                    </div>

                    <StatusBadge
                      status={
                        project.status ||
                        "Unknown"
                      }
                    />
                  </div>
                </section>

                <section className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                  <InfoCard
                    label="Company ID"
                    value={
                      project.company_id ??
                      "Not set"
                    }
                  />

                  <InfoCard
                    label="Department ID"
                    value={
                      project.department_id ??
                      "Not set"
                    }
                  />

                  <InfoCard
                    label="Team ID"
                    value={
                      project.team_id ??
                      "Not set"
                    }
                  />

                  <InfoCard
                    label="Created By"
                    value={
                      project.created_by ??
                      "Not set"
                    }
                  />
                </section>

                <section className="mt-6 grid gap-6 lg:grid-cols-3">
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-lg font-bold">
                          Project Progress
                        </h3>

                        <p className="mt-1 text-sm text-slate-500">
                          Current completion status
                        </p>
                      </div>

                      <span className="text-2xl font-bold text-blue-600">
                        {project.progress ??
                          0}
                        %
                      </span>
                    </div>

                    <div className="mt-6 h-3 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-blue-600 transition-all"
                        style={{
                          width: `${Math.min(
                            Math.max(
                              project.progress ??
                                0,
                              0
                            ),
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h3 className="text-lg font-bold">
                      Status
                    </h3>

                    <div className="mt-5">
                      <StatusBadge
                        status={
                          project.status ||
                          "Unknown"
                        }
                      />
                    </div>

                    <p className="mt-5 text-sm text-slate-500">
                      {project.is_active ===
                      false
                        ? "Project is inactive."
                        : "Project is active."}
                    </p>
                  </div>
                </section>

                <section className="mt-6 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                  <h3 className="text-lg font-bold">
                    Timeline
                  </h3>

                  <div className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
                    <TimelineItem
                      label="Start Date"
                      value={formatDate(
                        project.start_date
                      )}
                    />

                    <TimelineItem
                      label="End Date"
                      value={formatDate(
                        project.end_date
                      )}
                    />

                    <TimelineItem
                      label="Created"
                      value={formatDate(
                        project.created_at
                      )}
                    />

                    <TimelineItem
                      label="Last Updated"
                      value={formatDate(
                        project.updated_at
                      )}
                    />
                  </div>
                </section>

                <section className="mt-6 grid gap-5 md:grid-cols-3">
                  <QuickAction
                    title="Tasks"
                    description="View and manage project tasks."
                  />

                  <QuickAction
                    title="Files"
                    description="Manage project documents and files."
                  />

                  <QuickAction
                    title="Team"
                    description="View members working on this project."
                  />
                </section>
              </>
            )}
        </main>
      </div>

      {showEditModal &&
        project && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
            <div className="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white shadow-2xl">
              <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-6 py-5">
                <div>
                  <h2 className="text-xl font-bold">
                    Edit Project
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Update project details.
                  </p>
                </div>

                <button
                  type="button"
                  onClick={
                    closeEditModal
                  }
                  disabled={saving}
                  className="flex h-10 w-10 items-center justify-center rounded-xl bg-slate-100 text-xl text-slate-500"
                >
                  ×
                </button>
              </div>

              <form
                onSubmit={
                  updateProject
                }
                className="p-6"
              >
                {editError && (
                  <div className="mb-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
                    {editError}
                  </div>
                )}

                <div className="grid gap-5 sm:grid-cols-2">
                  <div className="sm:col-span-2">
                    <label
                      className={
                        labelClass
                      }
                    >
                      Project Name *
                    </label>

                    <input
                      type="text"
                      value={form.name}
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "name",
                          event.target
                            .value
                        )
                      }
                      className={
                        inputClass
                      }
                      required
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <label
                      className={
                        labelClass
                      }
                    >
                      Description
                    </label>

                    <textarea
                      value={
                        form.description
                      }
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "description",
                          event.target
                            .value
                        )
                      }
                      rows={4}
                      className={`${inputClass} h-auto resize-none py-3`}
                    />
                  </div>

                  <div>
                    <label
                      className={
                        labelClass
                      }
                    >
                      Company ID *
                    </label>

                    <input
                      type="number"
                      min="1"
                      value={
                        form.company_id
                      }
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "company_id",
                          event.target
                            .value
                        )
                      }
                      className={
                        inputClass
                      }
                      required
                    />
                  </div>

                  <div>
                    <label
                      className={
                        labelClass
                      }
                    >
                      Department ID
                    </label>

                    <input
                      type="number"
                      min="1"
                      value={
                        form.department_id
                      }
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "department_id",
                          event.target
                            .value
                        )
                      }
                      placeholder="Optional"
                      className={
                        inputClass
                      }
                    />
                  </div>

                  <div>
                    <label
                      className={
                        labelClass
                      }
                    >
                      Team ID
                    </label>

                    <input
                      type="number"
                      min="1"
                      value={
                        form.team_id
                      }
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "team_id",
                          event.target
                            .value
                        )
                      }
                      placeholder="Optional"
                      className={
                        inputClass
                      }
                    />
                  </div>

                  <div>
                    <label
                      className={
                        labelClass
                      }
                    >
                      Status
                    </label>

                    <select
                      value={
                        form.status
                      }
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "status",
                          event.target
                            .value
                        )
                      }
                      className={
                        inputClass
                      }
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
                    <label
                      className={
                        labelClass
                      }
                    >
                      Start Date
                    </label>

                    <input
                      type="date"
                      value={
                        form.start_date
                      }
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "start_date",
                          event.target
                            .value
                        )
                      }
                      className={
                        inputClass
                      }
                    />
                  </div>

                  <div>
                    <label
                      className={
                        labelClass
                      }
                    >
                      End Date
                    </label>

                    <input
                      type="date"
                      value={
                        form.end_date
                      }
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "end_date",
                          event.target
                            .value
                        )
                      }
                      className={
                        inputClass
                      }
                    />
                  </div>

                  <div className="sm:col-span-2">
                    <div className="flex items-center justify-between">
                      <label
                        className={
                          labelClass
                        }
                      >
                        Progress
                      </label>

                      <span className="text-sm font-bold text-blue-600">
                        {
                          form.progress
                        }
                        %
                      </span>
                    </div>

                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="1"
                      value={
                        form.progress
                      }
                      onChange={(
                        event
                      ) =>
                        updateForm(
                          "progress",
                          event.target
                            .value
                        )
                      }
                      className="mt-2 w-full accent-blue-600"
                    />
                  </div>
                </div>

                <div className="mt-7 flex justify-end gap-3 border-t border-slate-100 pt-5">
                  <button
                    type="button"
                    onClick={
                      closeEditModal
                    }
                    disabled={saving}
                    className="rounded-xl border border-slate-200 px-5 py-2.5 text-sm font-semibold text-slate-700 disabled:opacity-60"
                  >
                    Cancel
                  </button>

                  <button
                    type="submit"
                    disabled={saving}
                    className="rounded-xl bg-blue-600 px-6 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-60"
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

      {showDeleteModal &&
        project && (
          <div className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950/60 p-4 backdrop-blur-sm">
            <div className="w-full max-w-md rounded-3xl bg-white p-6 shadow-2xl">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-100 text-2xl font-bold text-red-600">
                !
              </div>

              <h2 className="mt-5 text-xl font-bold text-slate-900">
                Delete Project?
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-500">
                Are you sure you want to delete{" "}
                <span className="font-bold text-slate-800">
                  {project.name}
                </span>
                ?
              </p>

              <p className="mt-2 text-sm leading-6 text-red-600">
                This action cannot be undone.
              </p>

              {deleteError && (
                <div className="mt-5 rounded-xl border border-red-200 bg-red-50 p-3 text-sm font-medium text-red-700">
                  {deleteError}
                </div>
              )}

              <div className="mt-7 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={
                    closeDeleteModal
                  }
                  disabled={deleting}
                  className="rounded-xl border border-slate-200 bg-white px-5 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-60"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={
                    deleteProject
                  }
                  disabled={deleting}
                  className="rounded-xl bg-red-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-red-700 disabled:opacity-60"
                >
                  {deleting
                    ? "Deleting..."
                    : "Delete Project"}
                </button>
              </div>
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

function InfoCard({
  label,
  value,
}: {
  label: string;
  value: string | number;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-xl font-bold text-slate-900">
        {value}
      </p>
    </div>
  );
}

function TimelineItem({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div>
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {label}
      </p>

      <p className="mt-2 text-sm font-semibold text-slate-700">
        {value}
      </p>
    </div>
  );
}

function QuickAction({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 font-bold text-blue-600">
        {title.charAt(0)}
      </div>

      <h3 className="mt-4 font-bold">
        {title}
      </h3>

      <p className="mt-2 text-sm leading-5 text-slate-500">
        {description}
      </p>
    </div>
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
      "bg-emerald-100 text-emerald-700";
  } else if (
    normalized === "in progress"
  ) {
    classes =
      "bg-blue-100 text-blue-700";
  } else if (
    normalized === "planned"
  ) {
    classes =
      "bg-violet-100 text-violet-700";
  } else if (
    normalized === "on hold"
  ) {
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
      className={`inline-flex rounded-full px-3 py-1.5 text-xs font-bold ${classes}`}
    >
      {status}
    </span>
  );
}

function formatDate(
  value?: string | null
) {
  if (!value) {
    return "Not set";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
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

function toInputDate(
  value?: string | null
) {
  if (!value) {
    return "";
  }

  const date =
    new Date(value);

  if (
    Number.isNaN(
      date.getTime()
    )
  ) {
    return "";
  }

  const year =
    date.getFullYear();

  const month =
    String(
      date.getMonth() + 1
    ).padStart(2, "0");

  const day =
    String(
      date.getDate()
    ).padStart(2, "0");

  return `${year}-${month}-${day}`;
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

    if (
      typeof detail === "string"
    ) {
      return detail;
    }

    if (
      Array.isArray(detail)
    ) {
      const messages =
        detail
          .map((item) => {
            if (
              typeof item ===
                "object" &&
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

      if (
        messages.length > 0
      ) {
        return messages.join(
          ", "
        );
      }
    }
  }

  return fallback;
}

const labelClass =
  "mb-2 block text-sm font-semibold text-slate-700";

const inputClass =
  "h-11 w-full rounded-xl border border-slate-200 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10";