import { Zone, FileResult, Job, JobUpdate, ResizeOption } from "./types";

export const getZones = (): Promise<Zone[]> => {
  return fetch("/api/zones").then((r) => r.json());
};

export const createZone = (zoneData: {
  id: string;
  label: string;
  description?: string;
  quality: number;
  color?: string;
  resize?: ResizeOption;
}): Promise<Zone> => {
  return fetch("/api/zones", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(zoneData),
  }).then((r) => {
    if (!r.ok) throw new Error("Failed to create zone");
    return r.json();
  });
};

export const updateZone = (
  zoneId: string,
  zoneData: {
    id: string;
    label: string;
    description?: string;
    quality: number;
    color?: string;
    resize?: ResizeOption;
  },
): Promise<Zone> => {
  return fetch(`/api/zones/${zoneId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(zoneData),
  }).then((r) => {
    if (!r.ok) throw new Error("Failed to update zone");
    return r.json();
  });
};

export const deleteZone = (zoneId: string): Promise<void> => {
  return fetch(`/api/zones/${zoneId}`, {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
  }).then((r) => {
    if (!r.ok) throw new Error("Failed to delete zone");
  });
};

export const uploadFiles = (
  zoneId: string,
  files: File[],
  resize?: ResizeOption,
  outputPath?: string,
): Promise<{ job_id: string; total: number }> => {
  const form = new FormData();
  files.forEach((f) => form.append("files", f));

  if (resize && resize.mode) {
    form.append("use_resize", "true");
    form.append("mode", resize.mode);
    if (resize.ratio !== undefined && resize.ratio !== null)
      form.append("ratio", resize.ratio.toString());
    if (
      resize.long_side_length !== undefined &&
      resize.long_side_length !== null
    )
      form.append("long_side_length", resize.long_side_length.toString());
  } else {
    form.append("use_resize", "false");
  }

  if (outputPath) {
    form.append("output_path", outputPath);
  }

  // FormData 내용 확인용 (디버깅)
  console.log("api data:");
  for (const [key, value] of form.entries()) {
    console.log(`  ${key}: ${value}`);
  }
  const url = `/api/upload/${zoneId}`;
  return fetch(url, {
    method: "POST",
    body: form,
  }).then((r) => r.json());
};

export const getJobStatus = (jobId: string): Promise<Job> => {
  return fetch(`/api/jobs/${jobId}`).then((r) => r.json());
};

export const connectJobWS = (
  jobId: string,
  onMessage: (update: JobUpdate) => void,
): WebSocket => {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(
    `${protocol}://${window.location.host}/api/jobs/ws/${jobId}`,
  );
  ws.onmessage = (evt) => {
    const update = JSON.parse(evt.data);
    onMessage(update);
  };
  return ws;
};

export const updateZoneOrder = (
  zoneId: string, order: number
): Promise<Zone[]> => {
  return fetch("/api/zones/reorder", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      zoneId: zoneId,
      order: order,
  })
  }).then((r) => {
    if (!r.ok) throw new Error("Failed to update zone order");
    return r.json();
  });
};

export const downloadFile = async (
  jobId: string,
  filename: string,
): Promise<Blob> => {
  const response = await fetch(`/api/jobs/${jobId}/file/${filename}`);
  if (!response.ok) {
    throw new Error(`Failed to download file: ${filename}`);
  }
  return response.blob();
};

export const saveFileToLocal = async (
  blob: Blob,
  suggestedName: string,
): Promise<string> => {
  try {
    // File System Access API 지원 확인
    if (!("showDirectoryPicker" in window)) {
      throw new Error("File System Access API not supported in this browser");
    }

    // 사용자가 디렉토리 선택
    const dirHandle = await (window as any).showDirectoryPicker();

    // 파일 생성
    const fileHandle = await dirHandle.getFileHandle(suggestedName, {
      create: true,
    });
    const writable = await fileHandle.createWritable();
    await writable.write(blob);
    await writable.close();

    return suggestedName;
  } catch (error) {
    if ((error as Error).name === "AbortError") {
      throw new Error("Save cancelled");
    }
    throw error;
  }
};
