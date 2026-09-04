"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = "http://127.0.0.1:8000";

type DashboardStats = {
  total_projects: number;
  total_tasks: number;
  total_subtasks: number;
  total_comments: number;
  total_files: number;
  total_notifications: number;
  total_progress_updates: number;
};

type Task = {
  id?: number;
  name?: string;
  title?: string;
  status?: string;
  priority?: string;
  due_date?: string | null;
};

type Notification = {
  id?: number;
  title?: string;
  message?: string;
  notification_type?: string;
  type?: string;
  is_read?: boolean;
  created_at?: string;
};

const EMPTY_STATS: DashboardStats = {
  total_projects: 0,
  total_tasks: 0,
  total_subtasks: 0,
  total_comments: 0,
  total_files: 0,
  total_notifications: 0,
  total_progress_updates: 0,
};

export default function DashboardPage() {
  const router = useRouter();

  const [stats, setStats] =
    useState<DashboardStats>(EMPTY_STATS);

  const [tasks, setTasks] =
    useState<Task[]>([]);

  const [notifications, setNotifications] =
    useState<Notification[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [sidebarOpen, setSidebarOpen] =
    useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  function getAccessToken() {
    if (typeof window === "undefined") {
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

  async function authenticatedFetch(
    url: string
  ) {
    const token = getAccessToken();

    if (!token) {
      clearAuth();
      router.replace("/");

      throw new Error(
        "Authentication required."
      );
    }

    const response = await fetch(url, {
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
      },
      cache: "no-store",
    });

    if (response.status === 401) {
      clearAuth();
      router.replace("/");

      throw new Error(
        "Your session has expired."
      );
    }

    if (!response.ok) {
      throw new Error(
        `Request failed with status ${response.status}.`
      );
    }

    return response.json();
  }

  async function loadDashboard() {
    setLoading(true);
    setError("");

    try {
      const [
        statsData,
        tasksData,
        notificationsData,
      ] = await Promise.all([
        authenticatedFetch(
          `${API_BASE_URL}/api/v1/dashboard/stats`
        ),

        authenticatedFetch(
          `${API_BASE_URL}/api/v1/dashboard/recent-tasks?limit=5`
        ),

        authenticatedFetch(
          `${API_BASE_URL}/api/v1/dashboard/recent-notifications?limit=5`
        ),
      ]);

      setStats({
        total_projects: Number(
          statsData?.total_projects ?? 0
        ),

        total_tasks: Number(
          statsData?.total_tasks ?? 0
        ),

        total_subtasks: Number(
          statsData?.total_subtasks ?? 0
        ),

        total_comments: Number(
          statsData?.total_comments ?? 0
        ),

        total_files: Number(
          statsData?.total_files ?? 0
        ),

        total_notifications: Number(
          statsData?.total_notifications ?? 0
        ),

        total_progress_updates: Number(
          statsData?.total_progress_updates ?? 0
        ),
      });

      setTasks(
        Array.isArray(tasksData)
          ? tasksData
          : []
      );

      setNotifications(
        Array.isArray(notificationsData)
          ? notificationsData
          : []
      );
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError(
          "Unable to load dashboard."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    clearAuth();
    router.replace("/");
  }

  function navigateTo(path: string) {
    setSidebarOpen(false);
    router.push(path);
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          onClick={() =>
            setSidebarOpen(false)
          }
          className="fixed inset-0 z-30 bg-slate-950/40 lg:hidden"
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-72 transform flex-col border-r border-slate-800 bg-[#101828] text-white transition-transform duration-300 lg:translate-x-0 ${
          sidebarOpen
            ? "translate-x-0"
            : "-translate-x-full"
        }`}
      >
        {/* Logo */}
        <div className="flex h-20 items-center border-b border-white/10 px-6">
          <div className="flex items-center gap-3">

            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold shadow-lg shadow-blue-900/30">
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

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4">

          <SidebarSection title="WORKSPACE">

            <SidebarItem
              label="Dashboard"
              active
              icon={<DashboardIcon />}
              onClick={() =>
                navigateTo("/dashboard")
              }
            />

            <SidebarItem
              label="Projects"
              icon={<FolderIcon />}
              onClick={() =>
                navigateTo("/projects")
              }
            />

            <SidebarItem
              label="Tasks"
              icon={<TaskIcon />}
            />

            <SidebarItem
              label="Calendar"
              icon={<CalendarIcon />}
            />

          </SidebarSection>

          <SidebarSection title="COLLABORATION">

            <SidebarItem
              label="Chat"
              icon={<ChatIcon />}
            />

            <SidebarItem
              label="Files"
              icon={<FileIcon />}
            />

            <SidebarItem
              label="Notifications"
              icon={<BellIcon />}
              badge={
                stats.total_notifications
              }
            />

          </SidebarSection>

          <SidebarSection title="INTELLIGENCE">

            <SidebarItem
              label="AI Assistant"
              icon={<SparkIcon />}
            />

            <SidebarItem
              label="Reports"
              icon={<ChartIcon />}
            />

            <SidebarItem
              label="Advanced Search"
              icon={<SearchIcon />}
            />

          </SidebarSection>

        </nav>

        {/* User */}
        <div className="border-t border-white/10 p-4">

          <div className="mb-3 flex items-center gap-3 rounded-xl bg-white/5 p-3">

            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-blue-600 font-semibold">
              A
            </div>

            <div className="min-w-0 flex-1">

              <p className="truncate text-sm font-semibold">
                TreeFlow User
              </p>

              <p className="truncate text-xs text-slate-400">
                Workspace member
              </p>

            </div>

          </div>

          <button
            type="button"
            onClick={logout}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium text-slate-300 transition hover:bg-red-500/10 hover:text-red-300"
          >
            <LogoutIcon />
            Sign out
          </button>

        </div>
      </aside>

      {/* Main Area */}
      <div className="lg:pl-72">

        {/* Header */}
        <header className="sticky top-0 z-20 flex h-20 items-center justify-between border-b border-slate-200 bg-white/90 px-4 backdrop-blur sm:px-6 lg:px-8">

          <div className="flex items-center gap-4">

            <button
              type="button"
              onClick={() =>
                setSidebarOpen(true)
              }
              className="rounded-lg border border-slate-200 p-2 text-slate-600 lg:hidden"
            >
              <MenuIcon />
            </button>

            <div>
              <h2 className="text-lg font-bold sm:text-xl">
                Dashboard
              </h2>

              <p className="hidden text-sm text-slate-500 sm:block">
                Monitor your workspace from
                one place.
              </p>
            </div>

          </div>

          <div className="flex items-center gap-3">

            <button
              type="button"
              onClick={loadDashboard}
              className="hidden h-10 items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 sm:flex"
            >
              <RefreshIcon />
              Refresh
            </button>

            <button
              type="button"
              className="relative flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-600 transition hover:bg-slate-50"
            >
              <BellIcon />

              {stats.total_notifications >
                0 && (
                <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white">
                  {stats.total_notifications >
                  99
                    ? "99+"
                    : stats.total_notifications}
                </span>
              )}
            </button>

            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
              A
            </div>

          </div>

        </header>

        <main className="p-4 sm:p-6 lg:p-8">

          {/* Welcome */}
          <section className="mb-8 overflow-hidden rounded-3xl bg-[#101828] p-6 text-white shadow-xl shadow-slate-900/5 sm:p-8">

            <div className="relative">

              <div className="absolute -right-20 -top-28 h-64 w-64 rounded-full bg-blue-500/20 blur-3xl" />

              <div className="absolute -bottom-28 right-52 h-56 w-56 rounded-full bg-purple-500/20 blur-3xl" />

              <div className="relative z-10">

                <span className="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-blue-200">
                  TREEFLOW WORKSPACE
                </span>

                <h1 className="mt-4 text-2xl font-bold sm:text-3xl">
                  Welcome back 👋
                </h1>

                <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300 sm:text-base">
                  Here&apos;s what&apos;s
                  happening across your
                  projects, tasks and
                  workspace today.
                </p>

              </div>

            </div>

          </section>

          {/* Error */}
          {error && (
            <div className="mb-6 flex items-center justify-between gap-4 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">

              <span>{error}</span>

              <button
                type="button"
                onClick={loadDashboard}
                className="shrink-0 font-semibold underline"
              >
                Retry
              </button>

            </div>
          )}

          {/* Main Stats */}
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

            <StatCard
              title="Total Projects"
              value={
                stats.total_projects
              }
              helper="Accessible projects"
              icon={<FolderIcon />}
              loading={loading}
            />

            <StatCard
              title="Total Tasks"
              value={stats.total_tasks}
              helper="Across your projects"
              icon={<TaskIcon />}
              loading={loading}
            />

            <StatCard
              title="Files"
              value={stats.total_files}
              helper="Workspace files"
              icon={<FileIcon />}
              loading={loading}
            />

            <StatCard
              title="Notifications"
              value={
                stats.total_notifications
              }
              helper="Your notifications"
              icon={<BellIcon />}
              loading={loading}
            />

          </section>

          {/* Secondary Stats */}
          <section className="mt-4 grid gap-4 sm:grid-cols-3">

            <MiniStat
              label="Subtasks"
              value={
                stats.total_subtasks
              }
              loading={loading}
            />

            <MiniStat
              label="Comments"
              value={
                stats.total_comments
              }
              loading={loading}
            />

            <MiniStat
              label="Progress Updates"
              value={
                stats.total_progress_updates
              }
              loading={loading}
            />

          </section>

          {/* Tasks + Notifications */}
          <section className="mt-8 grid gap-6 xl:grid-cols-[1.45fr_1fr]">

            {/* Recent Tasks */}
            <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

              <div className="flex items-center justify-between border-b border-slate-100 p-5 sm:p-6">

                <div>

                  <h3 className="font-bold text-slate-900">
                    Recent Tasks
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    Latest tasks from your
                    accessible projects.
                  </p>

                </div>

                <button
                  type="button"
                  className="text-sm font-semibold text-blue-600 hover:text-blue-700"
                >
                  View all
                </button>

              </div>

              <div className="divide-y divide-slate-100">

                {loading ? (
                  <>
                    <TaskSkeleton />
                    <TaskSkeleton />
                    <TaskSkeleton />
                  </>
                ) : tasks.length > 0 ? (
                  tasks.map(
                    (task, index) => (
                      <TaskRow
                        key={
                          task.id ??
                          index
                        }
                        task={task}
                      />
                    )
                  )
                ) : (
                  <EmptyState
                    title="No tasks found"
                    text="Recent tasks will appear here."
                    icon={<TaskIcon />}
                  />
                )}

              </div>

            </div>

            {/* Notifications */}
            <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">

              <div className="flex items-center justify-between border-b border-slate-100 p-5 sm:p-6">

                <div>

                  <h3 className="font-bold text-slate-900">
                    Recent Notifications
                  </h3>

                  <p className="mt-1 text-sm text-slate-500">
                    Latest workspace
                    updates.
                  </p>

                </div>

                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  <BellIcon />
                </div>

              </div>

              <div className="divide-y divide-slate-100">

                {loading ? (
                  <>
                    <NotificationSkeleton />
                    <NotificationSkeleton />
                    <NotificationSkeleton />
                  </>
                ) : notifications.length >
                  0 ? (
                  notifications.map(
                    (
                      notification,
                      index
                    ) => (
                      <NotificationRow
                        key={
                          notification.id ??
                          index
                        }
                        notification={
                          notification
                        }
                      />
                    )
                  )
                ) : (
                  <EmptyState
                    title="No notifications"
                    text="You're all caught up."
                    icon={<BellIcon />}
                  />
                )}

              </div>

            </div>

          </section>

          {/* Quick Access */}
          <section className="mt-8">

            <div className="mb-4">

              <h3 className="text-lg font-bold">
                Quick Access
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Jump into the tools you
                use most.
              </p>

            </div>

            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

              <QuickCard
                title="Projects"
                description="Manage your projects"
                icon={<FolderIcon />}
                onClick={() =>
                  router.push(
                    "/projects"
                  )
                }
              />

              <QuickCard
                title="Tasks"
                description="Track your work"
                icon={<TaskIcon />}
              />

              <QuickCard
                title="Files"
                description="Browse workspace files"
                icon={<FileIcon />}
              />

              <QuickCard
                title="AI Assistant"
                description="Get smart assistance"
                icon={<SparkIcon />}
              />

            </div>

          </section>

        </main>

      </div>

    </div>
  );
}

/* =========================================================
   Sidebar Section
========================================================= */

function SidebarSection({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="mb-7">

      <p className="mb-2 px-3 text-[11px] font-bold tracking-[0.16em] text-slate-500">
        {title}
      </p>

      <div className="space-y-1">
        {children}
      </div>

    </div>
  );
}

/* =========================================================
   Sidebar Item
========================================================= */

function SidebarItem({
  label,
  icon,
  active = false,
  badge,
  onClick,
}: {
  label: string;
  icon: React.ReactNode;
  active?: boolean;
  badge?: number;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm font-medium transition ${
        active
          ? "bg-blue-600 text-white shadow-lg shadow-blue-900/20"
          : "text-slate-300 hover:bg-white/5 hover:text-white"
      }`}
    >

      <span className="shrink-0">
        {icon}
      </span>

      <span className="flex-1">
        {label}
      </span>

      {typeof badge === "number" &&
        badge > 0 && (
          <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px] font-bold">
            {badge > 99
              ? "99+"
              : badge}
          </span>
        )}

    </button>
  );
}

/* =========================================================
   Stat Card
========================================================= */

function StatCard({
  title,
  value,
  helper,
  icon,
  loading,
}: {
  title: string;
  value: number;
  helper: string;
  icon: React.ReactNode;
  loading: boolean;
}) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          {loading ? (
            <div className="mt-3 h-9 w-16 animate-pulse rounded-lg bg-slate-100" />
          ) : (
            <p className="mt-2 text-3xl font-bold tracking-tight">
              {value}
            </p>
          )}

        </div>

        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
          {icon}
        </div>

      </div>

      <p className="mt-4 text-xs text-slate-400">
        {helper}
      </p>

    </div>
  );
}

/* =========================================================
   Mini Stat
========================================================= */

function MiniStat({
  label,
  value,
  loading,
}: {
  label: string;
  value: number;
  loading: boolean;
}) {
  return (
    <div className="flex items-center justify-between rounded-2xl border border-slate-200 bg-white px-5 py-4 shadow-sm">

      <span className="text-sm font-medium text-slate-500">
        {label}
      </span>

      {loading ? (
        <div className="h-6 w-10 animate-pulse rounded bg-slate-100" />
      ) : (
        <span className="text-xl font-bold">
          {value}
        </span>
      )}

    </div>
  );
}

/* =========================================================
   Task Row
========================================================= */

function TaskRow({
  task,
}: {
  task: Task;
}) {
  const title =
    task.name ||
    task.title ||
    "Untitled task";

  return (
    <div className="flex items-center gap-4 p-5 transition hover:bg-slate-50 sm:p-6">

      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-slate-100 text-slate-600">
        <TaskIcon />
      </div>

      <div className="min-w-0 flex-1">

        <p className="truncate text-sm font-semibold text-slate-900">
          {title}
        </p>

        <div className="mt-2 flex flex-wrap items-center gap-2">

          {task.status && (
            <StatusBadge
              status={task.status}
            />
          )}

          {task.priority && (
            <PriorityBadge
              priority={
                task.priority
              }
            />
          )}

        </div>

      </div>

      <div className="hidden text-right sm:block">

        <p className="text-xs font-medium text-slate-400">
          Due date
        </p>

        <p className="mt-1 text-xs text-slate-600">
          {formatDate(
            task.due_date
          )}
        </p>

      </div>

    </div>
  );
}

/* =========================================================
   Notification Row
========================================================= */

function NotificationRow({
  notification,
}: {
  notification: Notification;
}) {
  return (
    <div className="flex gap-4 p-5 transition hover:bg-slate-50 sm:p-6">

      <div
        className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
          notification.is_read ===
          false
            ? "bg-blue-50 text-blue-600"
            : "bg-slate-100 text-slate-500"
        }`}
      >
        <BellIcon />
      </div>

      <div className="min-w-0 flex-1">

        <div className="flex items-start justify-between gap-3">

          <p className="text-sm font-semibold text-slate-900">
            {notification.title ||
              notification.notification_type ||
              notification.type ||
              "Notification"}
          </p>

          {notification.is_read ===
            false && (
            <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-blue-600" />
          )}

        </div>

        <p className="mt-1 line-clamp-2 text-sm leading-5 text-slate-500">
          {notification.message ||
            "Workspace notification"}
        </p>

        <p className="mt-2 text-xs text-slate-400">
          {formatDateTime(
            notification.created_at
          )}
        </p>

      </div>

    </div>
  );
}

/* =========================================================
   Status Badge
========================================================= */

function StatusBadge({
  status,
}: {
  status: string;
}) {
  const normalized = status
    .toLowerCase()
    .replaceAll(" ", "_");

  let classes =
    "bg-slate-100 text-slate-600";

  if (
    normalized.includes("done")
  ) {
    classes =
      "bg-emerald-50 text-emerald-700";
  } else if (
    normalized.includes("progress")
  ) {
    classes =
      "bg-blue-50 text-blue-700";
  } else if (
    normalized.includes("review")
  ) {
    classes =
      "bg-amber-50 text-amber-700";
  } else if (
    normalized.includes("cancel")
  ) {
    classes =
      "bg-red-50 text-red-700";
  }

  return (
    <span
      className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${classes}`}
    >
      {formatLabel(status)}
    </span>
  );
}

/* =========================================================
   Priority Badge
========================================================= */

function PriorityBadge({
  priority,
}: {
  priority: string;
}) {
  const normalized =
    priority.toLowerCase();

  let classes =
    "bg-slate-100 text-slate-600";

  if (
    normalized.includes("critical")
  ) {
    classes =
      "bg-red-50 text-red-700";
  } else if (
    normalized.includes("high")
  ) {
    classes =
      "bg-orange-50 text-orange-700";
  } else if (
    normalized.includes("medium")
  ) {
    classes =
      "bg-amber-50 text-amber-700";
  } else if (
    normalized.includes("low")
  ) {
    classes =
      "bg-emerald-50 text-emerald-700";
  }

  return (
    <span
      className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${classes}`}
    >
      {formatLabel(priority)}
    </span>
  );
}

/* =========================================================
   Quick Card
========================================================= */

function QuickCard({
  title,
  description,
  icon,
  onClick,
}: {
  title: string;
  description: string;
  icon: React.ReactNode;
  onClick?: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 text-left shadow-sm transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md"
    >

      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
        {icon}
      </div>

      <div>

        <p className="text-sm font-bold text-slate-900">
          {title}
        </p>

        <p className="mt-1 text-xs text-slate-500">
          {description}
        </p>

      </div>

    </button>
  );
}

/* =========================================================
   Empty State
========================================================= */

function EmptyState({
  title,
  text,
  icon,
}: {
  title: string;
  text: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center px-6 py-12 text-center">

      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-500">
        {icon}
      </div>

      <p className="mt-4 text-sm font-semibold text-slate-800">
        {title}
      </p>

      <p className="mt-1 text-sm text-slate-500">
        {text}
      </p>

    </div>
  );
}

/* =========================================================
   Skeletons
========================================================= */

function TaskSkeleton() {
  return (
    <div className="flex animate-pulse items-center gap-4 p-6">

      <div className="h-10 w-10 rounded-xl bg-slate-100" />

      <div className="flex-1">
        <div className="h-4 w-2/5 rounded bg-slate-100" />
        <div className="mt-3 h-3 w-1/4 rounded bg-slate-100" />
      </div>

    </div>
  );
}

function NotificationSkeleton() {
  return (
    <div className="flex animate-pulse gap-4 p-6">

      <div className="h-10 w-10 rounded-xl bg-slate-100" />

      <div className="flex-1">
        <div className="h-4 w-1/2 rounded bg-slate-100" />
        <div className="mt-3 h-3 w-full rounded bg-slate-100" />
        <div className="mt-2 h-3 w-1/3 rounded bg-slate-100" />
      </div>

    </div>
  );
}

/* =========================================================
   Formatting Helpers
========================================================= */

function formatDate(
  value?: string | null
) {
  if (!value) {
    return "No due date";
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

function formatDateTime(
  value?: string
) {
  if (!value) {
    return "Recently";
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
      hour: "2-digit",
      minute: "2-digit",
    }
  ).format(date);
}

function formatLabel(
  value: string
) {
  return value
    .replaceAll("_", " ")
    .replace(
      /\b\w/g,
      (letter) =>
        letter.toUpperCase()
    );
}

/* =========================================================
   Icons
========================================================= */

function BaseIcon({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-5 w-5"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

function DashboardIcon() {
  return (
    <BaseIcon>
      <rect
        x="3"
        y="3"
        width="7"
        height="7"
        rx="1"
      />
      <rect
        x="14"
        y="3"
        width="7"
        height="7"
        rx="1"
      />
      <rect
        x="3"
        y="14"
        width="7"
        height="7"
        rx="1"
      />
      <rect
        x="14"
        y="14"
        width="7"
        height="7"
        rx="1"
      />
    </BaseIcon>
  );
}

function FolderIcon() {
  return (
    <BaseIcon>
      <path d="M3 6.5a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
    </BaseIcon>
  );
}

function TaskIcon() {
  return (
    <BaseIcon>
      <rect
        x="4"
        y="3"
        width="16"
        height="18"
        rx="2"
      />
      <path d="m8 9 2 2 4-4" />
      <path d="M8 15h8" />
    </BaseIcon>
  );
}

function CalendarIcon() {
  return (
    <BaseIcon>
      <rect
        x="3"
        y="5"
        width="18"
        height="16"
        rx="2"
      />
      <path d="M16 3v4M8 3v4M3 10h18" />
    </BaseIcon>
  );
}

function ChatIcon() {
  return (
    <BaseIcon>
      <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z" />
    </BaseIcon>
  );
}

function FileIcon() {
  return (
    <BaseIcon>
      <path d="M6 2h8l4 4v16H6z" />
      <path d="M14 2v5h5" />
    </BaseIcon>
  );
}

function BellIcon() {
  return (
    <BaseIcon>
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9" />
      <path d="M10 21h4" />
    </BaseIcon>
  );
}

function SparkIcon() {
  return (
    <BaseIcon>
      <path d="m12 3 1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6z" />
      <path d="m19 15 .8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z" />
    </BaseIcon>
  );
}

function ChartIcon() {
  return (
    <BaseIcon>
      <path d="M4 20V10M10 20V4M16 20v-7M22 20H2" />
    </BaseIcon>
  );
}

function SearchIcon() {
  return (
    <BaseIcon>
      <circle
        cx="11"
        cy="11"
        r="7"
      />
      <path d="m20 20-4-4" />
    </BaseIcon>
  );
}

function LogoutIcon() {
  return (
    <BaseIcon>
      <path d="M10 17l5-5-5-5" />
      <path d="M15 12H3" />
      <path d="M14 3h5a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-5" />
    </BaseIcon>
  );
}

function MenuIcon() {
  return (
    <BaseIcon>
      <path d="M4 6h16M4 12h16M4 18h16" />
    </BaseIcon>
  );
}

function RefreshIcon() {
  return (
    <BaseIcon>
      <path d="M20 6v5h-5" />
      <path d="M4 18v-5h5" />
      <path d="M18 9a7 7 0 0 0-12-2L4 11" />
      <path d="M6 15a7 7 0 0 0 12 2l2-4" />
    </BaseIcon>
  );
}
