# Z-Image API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/tongyi/z-image-turbo)

Z-Image-Turbo is a 6-billion-parameter text-to-image model from Alibaba's Tongyi-MAI lab, distilled to produce a finished image in a handful of denoising steps. This package is a small Python client for the Z Image API hosted on Synexa: one `pip install`, one environment variable, and `run({"prompt": ...})` returns the URL of a generated image without any model weights or GPU on your side.

You get a blocking `run()` that waits for the result, a non-blocking mode you can poll, webhook delivery on completion, and typed errors. The only dependency is `httpx`. It is meant for backend services, batch jobs, notebooks and CI pipelines that need Z-Image output and do not want to operate inference servers.

> **Try it now:** [https://synexa.ai/explore/tongyi/z-image-turbo](https://synexa.ai/explore/tongyi/z-image-turbo) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About Z-Image](#about-z-image)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **No 16 GB card to find.** Z-Image-Turbo is advertised as fitting on a 16 GB consumer GPU, which still rules out most laptops, CI runners and serverless platforms. The hosted endpoint runs on datacenter hardware; you call HTTPS.
- **No weight download or environment build.** Self-hosting means pulling the checkpoint and matching PyTorch and diffusers versions. Here the setup is `pip install` plus `SYNEXA_API_KEY`.
- **No cold start.** A freshly booted GPU box spends minutes loading weights before the first image; the hosted model is already resident.
- **$0.002 per run, nothing while idle.** A thousand images cost two dollars and there is no bill between batches, unlike a GPU that is charged by the hour whether it renders or not.

## Installation

```bash
pip install git+https://github.com/zimage-dev/z-image-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import z_image_api

output = z_image_api.run({
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from z_image_api import Client

client = Client(api_key="sk-...")
output = client.run({"prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`tongyi/z-image-turbo`](https://synexa.ai/explore/tongyi/z-image-turbo) | text-to-image | Z-Image Turbo is a super fast text-to-image model of 6B parameters developed by Tongyi-MAI. | $0.002 |

The default model is **`tongyi/z-image-turbo`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `tongyi/z-image-turbo`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A hyper-realistic, close-up portrait of …` | — | Input prompt |
| `width` | integer | no | `1024` | 256, 1440 | Width of output image |
| `height` | integer | no | `1024` | 256, 1440 | Height of output image |
| `steps` | integer | no | `9` | 1, 10 | Number of denoising steps |
| `seed` | integer | no | `random` | — | Random seed. Leave blank to randomize the seed |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from z_image_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About Z-Image

Z-Image is a family of open text-to-image models published by Tongyi-MAI, the multimodal AI group inside Alibaba's Tongyi Lab, with code and weights released through the [Tongyi-MAI/Z-Image](https://github.com/Tongyi-MAI/Z-Image) repository. The family is built around a single-stream diffusion transformer with roughly 6 billion parameters, which is small next to the 12B-and-up class of recent image models, and it is notable for rendering legible text in both English and Chinese.

Z-Image-Turbo is the distilled member of the family. Instead of the 25–50 sampling steps a conventional diffusion model needs, Turbo is trained to converge in a few steps (the reference configuration uses eight), so a 1024×1024 image is produced in well under a second on a datacenter GPU and in a few seconds on a consumer card. The trade-off is that the guidance scale is baked into the distilled weights: you control the output with the prompt, resolution and seed rather than a CFG value.

The hosted endpoint exposes exactly those controls (`prompt`, `width`, `height`, `steps`, `seed`) and returns one image URL per run. As with any distilled model, very long or highly compositional prompts can lose detail compared with the undistilled base model, and there is no built-in inpainting or reference-image mode.

The endpoint used by this client is `tongyi/z-image-turbo`, which is the same Z-Image-Turbo model that Tongyi-MAI released, served on Synexa's GPUs. The weights and reference inference code are available in the official repository if you would rather run it yourself.

**Official project:** https://github.com/Tongyi-MAI/Z-Image

## Use cases

- **Product thumbnails at scale** — loop over a CSV of product names and call `run({"prompt": ..., "width": 1024, "height": 1024})` for each; at $0.002 a run the whole catalogue costs less than a coffee.
- **Bilingual marketing creatives** — Z-Image renders Chinese and English text in-image, so a prompt like `"poster with the headline '春季特惠' in bold red"` produces usable copy without a second design pass.
- **Placeholder and concept art for game or UI prototypes** — generate a batch with a fixed `seed` so the same prompt returns the same image across builds, then swap in final art later.
- **Interactive prompt playground in a web app** — submit with `wait=False`, return the prediction id to the browser, and poll from the frontend so the request thread never blocks.
- **Dataset augmentation** — generate labelled synthetic images from templated prompts (`"a photo of a {object} on a white background"`) for classifier pretraining.
- **Chat or Discord bots** — register a `/imagine` command that forwards the user's text as `prompt` and posts back the returned URL; the sub-second model keeps the bot feeling responsive.

## FAQ

**Is there a Z-Image API?**

There is no official REST API from Tongyi-MAI; the project ships weights and inference code. This package is a Python client for the hosted `tongyi/z-image-turbo` endpoint on Synexa, which serves the released model behind an HTTPS API.

**How much does the Z-Image API cost?**

The hosted endpoint is billed per prediction at $0.002 per run. There is no hourly charge and nothing to pay while you are not generating. New Synexa accounts receive a free trial credit.

**Can I run Z-Image without a GPU?**

Yes. With this client the model runs on Synexa's GPUs; your code only needs Python 3.8+, `httpx` and network access. Self-hosting Z-Image-Turbo requires a CUDA GPU with roughly 16 GB of VRAM.

**Does this client work with the official Tongyi-MAI/Z-Image repo or ComfyUI?**

No. It does not load local weights, ComfyUI workflows or diffusers pipelines. It sends `prompt`, `width`, `height`, `steps` and `seed` to the hosted endpoint and returns an image URL. If you need custom nodes, LoRAs or offline inference, use the official repository directly.

**What input formats does it accept?**

Input is a plain JSON object. `prompt` (string) is the only required field; `width` and `height` are integers in pixels, `steps` is an integer, and `seed` is an optional integer. Output is a URL to the generated image, which you can download with any HTTP library.

**Is this the official Z-Image SDK?**

No. This is an independent, MIT-licensed client and is not affiliated with Tongyi-MAI or Alibaba. The official project lives at https://github.com/Tongyi-MAI/Z-Image.

## Related

- [Tongyi-MAI/Z-Image](https://github.com/Tongyi-MAI/Z-Image) — official weights, inference code and model card.
- [Synexa Python client](https://github.com/synexa-ai/synexa-python) — the general-purpose client for every model on the platform.
- [black-forest-labs/flux-schnell](https://synexa.ai/explore/black-forest-labs/flux-schnell) — another few-step text-to-image model, useful for side-by-side comparison.
- [bytedance/sdxl-lightning-4step](https://synexa.ai/explore/bytedance/sdxl-lightning-4step) — 4-step SDXL distillation at a similar price point.
- [black-forest-labs/flux-kontext-pro](https://synexa.ai/explore/black-forest-labs/flux-kontext-pro) — when you need to edit an existing image rather than generate one.

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of Z-Image. Model weights and trademarks belong to their respective owners.
