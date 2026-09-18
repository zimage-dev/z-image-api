        """Minimal Z-Image example: create one prediction and print the output URL(s)."""
        import z_image_api

        output = z_image_api.run({
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light"
})
        print(output)
